import hashlib
import json
import os
import sys
from pathlib import Path
from typing import (NewType, Optional, cast)

import canonicaljson

from github_actions.api import GithubApi, IssueUrl, PrUrl
from github_actions.cache import ActionsCache
from github_actions.debug import debug
from github_actions.env import GithubEnv
from github_actions.find_pr import find_pr, WorkflowException
from github_actions.inputs import PlanPrInputs
from github_pr_comment.backend_config import complete_config
from github_pr_comment.backend_fingerprint import fingerprint
from github_pr_comment.comment import find_comment, TerraformComment, update_comment, serialize, deserialize
from terraform.module import load_module

Plan = NewType('Plan', str)
Status = NewType('Status', str)

job_cache = ActionsCache(Path(os.environ.get('JOB_TMP_DIR', '.')), 'job_cache')
step_cache = ActionsCache(Path(os.environ.get('STEP_TMP_DIR', '.')), 'step_cache')

env = cast(GithubEnv, os.environ)

github = GithubApi(env.get('GITHUB_API_URL', 'https://api.github.com'), env['GITHUB_TOKEN'])


def _mask_backend_config(action_inputs: PlanPrInputs) -> Optional[str]:
    bad_words = [
        'token',
        'password',
        'sas_token',
        'access_key',
        'secret_key',
        'client_secret',
        'access_token',
        'http_auth',
        'secret_id',
        'encryption_key',
        'key_material',
        'security_token',
        'conn_str',
        'sse_customer_key',
        'application_credential_secret'
    ]

    clean = []

    for field in action_inputs.get('INPUT_BACKEND_CONFIG', '').split(','):
        if not field:
            continue

        if not any(bad_word in field for bad_word in bad_words):
            clean.append(field)

    return ','.join(clean)


def format_classic_description(action_inputs: PlanPrInputs) -> str:
    if action_inputs['INPUT_LABEL']:
        return f'Terraform plan for __{action_inputs["INPUT_LABEL"]}__'

    label = f'Terraform plan in __{action_inputs["INPUT_PATH"]}__'

    if action_inputs["INPUT_WORKSPACE"] != 'default':
        label += f' in the __{action_inputs["INPUT_WORKSPACE"]}__ workspace'

    if action_inputs["INPUT_TARGET"]:
        label += '\nTargeting resources: '
        label += ', '.join(f'`{res.strip()}`' for res in action_inputs['INPUT_TARGET'].splitlines())

    if action_inputs["INPUT_REPLACE"]:
        label += '\nReplacing resources: '
        label += ', '.join(f'`{res.strip()}`' for res in action_inputs['INPUT_REPLACE'].splitlines())

    if backend_config := _mask_backend_config(action_inputs):
        label += f'\nWith backend config: `{backend_config}`'

    if action_inputs["INPUT_BACKEND_CONFIG_FILE"]:
        label += f'\nWith backend config files: `{action_inputs["INPUT_BACKEND_CONFIG_FILE"]}`'

    if action_inputs["INPUT_VAR"]:
        label += f'\nWith vars: `{action_inputs["INPUT_VAR"]}`'

    if action_inputs["INPUT_VAR_FILE"]:
        label += f'\nWith var files: `{action_inputs["INPUT_VAR_FILE"]}`'

    if action_inputs["INPUT_VARIABLES"]:
        stripped_vars = action_inputs["INPUT_VARIABLES"].strip()
        if '\n' in stripped_vars:
            label += f'''<details><summary>With variables</summary>

```hcl
{stripped_vars}
```
</details>
'''
        else:
            label += f'\nWith variables: `{stripped_vars}`'

    return label


def create_summary(plan: Plan) -> Optional[str]:
    summary = None

    for line in plan.splitlines():
        if line.startswith('No changes') or line.startswith('Error'):
            return line

        if line.startswith('Plan:'):
            summary = line

        if line.startswith('Changes to Outputs'):
            if summary:
                return summary + ' Changes to Outputs.'
            else:
                return 'Changes to Outputs'

    return summary


def current_user(actions_env: GithubEnv) -> str:
    token_hash = hashlib.sha256(actions_env['GITHUB_TOKEN'].encode()).hexdigest()
    cache_key = f'token-cache/{token_hash}'

    if cache_key in job_cache:
        username = job_cache[cache_key]
    else:
        response = github.get(f'{actions_env["GITHUB_API_URL"]}/user')
        if response.status_code != 403:
            user = response.json()
            debug(json.dumps(user))

            username = user['login']
        else:
            # Assume this is the github actions app token
            username = 'github-actions[bot]'

        job_cache[cache_key] = username

    return username


def get_issue_url(pr_url: str) -> IssueUrl:
    pr_hash = hashlib.sha256(pr_url.encode()).hexdigest()
    cache_key = f'issue-href-cache/{pr_hash}'

    if cache_key in job_cache:
        issue_url = job_cache[cache_key]
    else:
        response = github.get(pr_url)
        response.raise_for_status()
        issue_url = response.json()['_links']['issue']['href'] + '/comments'

        job_cache[cache_key] = issue_url

    return cast(IssueUrl, issue_url)


def get_pr() -> PrUrl:
    if 'pr_url' in step_cache:
        pr_url = step_cache['pr_url']
    else:
        try:
            pr_url = find_pr(github, env)
            step_cache['pr_url'] = pr_url
        except WorkflowException as e:
            sys.stderr.write('\n' + str(e) + '\n')
            sys.exit(1)

    return cast(PrUrl, pr_url)

def comment_hash(value: bytes, salt: str) -> str:
    h = hashlib.sha256(f'dflook/terraform-github-actions/{salt}'.encode())
    h.update(value)
    return h.hexdigest()

def get_comment(action_inputs: PlanPrInputs, backend_fingerprint: bytes) -> TerraformComment:
    if 'comment' in step_cache:
        return deserialize(step_cache['comment'])

    pr_url = get_pr()
    issue_url = get_issue_url(pr_url)
    username = current_user(env)

    legacy_description = format_classic_description(action_inputs)

    headers = {
        'workspace': os.environ.get('INPUT_WORKSPACE', 'default'),
        'backend': comment_hash(backend_fingerprint, pr_url)
    }

    if backend_type := os.environ.get('TERRAFORM_BACKEND_TYPE'):
        headers['backend_type'] = backend_type

    headers['label'] = os.environ.get('INPUT_LABEL') or None

    plan_modifier = {}
    if target := os.environ.get('INPUT_TARGET'):
        plan_modifier['target'] = sorted(t.strip() for t in target.replace(',', '\n', ).split('\n') if t.strip())

    if replace := os.environ.get('INPUT_REPLACE'):
        plan_modifier['replace'] = sorted(t.strip() for t in replace.replace(',', '\n', ).split('\n') if t.strip())

    if plan_modifier:
        debug(f'Plan modifier: {plan_modifier}')
        headers['plan_modifier'] = hashlib.sha256(canonicaljson.encode_canonical_json(plan_modifier)).hexdigest()

    return find_comment(github, issue_url, username, headers, legacy_description)

def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write(f'''Usage:
    STATUS="<status>" {sys.argv[0]} plan <plan.txt
    STATUS="<status>" {sys.argv[0]} status
    {sys.argv[0]} get plan.txt
''')
        return 1

    debug(repr(sys.argv))

    action_inputs = cast(PlanPrInputs, os.environ)

    module = load_module(Path(action_inputs.get('INPUT_PATH', '.')))

    backend_type, backend_config = complete_config(action_inputs, module)

    backend_fingerprint = fingerprint(backend_type, backend_config, os.environ)

    comment = get_comment(action_inputs, backend_fingerprint)

    status = cast(Status, os.environ.get('STATUS', ''))

    if sys.argv[1] == 'plan':
        body = cast(Plan, sys.stdin.read().strip())
        description = format_classic_description(action_inputs)

        only_if_exists = False
        if action_inputs['INPUT_ADD_GITHUB_COMMENT'] == 'changes-only' and os.environ.get('TF_CHANGES', 'true') == 'false':
            only_if_exists = True

        if comment.comment_url is None and only_if_exists:
            debug('Comment doesn\'t already exist - not creating it')
            return 0

        comment = update_comment(
            github,
            comment,
            description=description,
            summary=create_summary(body),
            body=body,
            status=status
        )

    elif sys.argv[1] == 'status':
        if comment.comment_url is None:
            debug("Can't set status of comment that doesn't exist")
            return 1
        else:
            comment = update_comment(github, comment, status=status)

    elif sys.argv[1] == 'get':
        if comment.comment_url is None:
            debug("Can't get the plan from comment that doesn't exist")
            return 1

        with open(sys.argv[2], 'w') as f:
            f.write(comment.body)

    step_cache['comment'] = serialize(comment)
    return 0

if __name__ == '__main__':
    sys.exit(main())
