#!/usr/bin/python3

import hashlib
import json
import os
import re
import sys
from typing import (NewType, Optional, Tuple, cast)

from github_actions.api import GithubApi, IssueUrl, CommentUrl
from github_actions.cache import ActionsCache
from github_actions.debug import debug
from github_actions.env import GithubEnv
from github_actions.find_pr import find_pr
from github_actions.inputs import PlanPrInputs

Plan = NewType('Plan', str)
Status = NewType('Status', str)

job_cache = ActionsCache(os.environ.get('JOB_TMP_DIR', '.'))
step_cache = ActionsCache(os.environ.get('STEP_TMP_DIR', '.'))

env = cast(GithubEnv, os.environ)

github = GithubApi(env['GITHUB_API_URL'], env['GITHUB_TOKEN'])


def plan_identifier(action_inputs: PlanPrInputs) -> str:
    def mask_backend_config() -> Optional[str]:

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

        def has_bad_word(s: str) -> bool:
            for bad_word in bad_words:
                if bad_word in s:
                    return True
            return False

        clean = []

        for field in action_inputs.get('INPUT_BACKEND_CONFIG', '').split(','):
            if not field:
                continue

            if not has_bad_word(field):
                clean.append(field)

        return ','.join(clean)

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

    backend_config = mask_backend_config()
    if backend_config:
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


def current_user(actions_env: GithubEnv) -> str:
    token_hash = hashlib.sha256(actions_env['GITHUB_TOKEN'].encode()).hexdigest()

    def get():
        response = github.get(f'{actions_env["GITHUB_API_URL"]}/user')
        if response.status_code != 403:
            user = response.json()
            debug(json.dumps(user))

            return user['login']
        else:
            # Assume this is the github actions app token
            return 'github-actions[bot]'

    username = job_cache.get_default_func(f'token-cache/{token_hash}', get)
    debug(f'discovered GITHUB_TOKEN username: {username}')
    return username


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


def format_body(action_inputs: PlanPrInputs, plan: Plan, status: Status, collapse_threshold: int) -> str:
    details_open = ''
    highlighting = ''

    summary_line = create_summary(plan)

    if plan.startswith('Error'):
        details_open = ' open'
    elif 'Plan:' in plan:
        highlighting = 'hcl'
        num_lines = len(plan.splitlines())
        if num_lines < collapse_threshold:
            details_open = ' open'

    if summary_line is None:
        details_open = ' open'

    body = f'''{plan_identifier(action_inputs)}
<details{details_open}>
{f'<summary>{summary_line}</summary>' if summary_line is not None else ''}

```{highlighting}
{plan}
```
</details>
'''

    if status:
        body += '\n' + status

    return body


def update_comment(issue_url: IssueUrl,
                   comment_url: Optional[CommentUrl],
                   body: str,
                   only_if_exists: bool = False) -> Optional[CommentUrl]:
    """
    Update (or create) a comment

    :param issue_url: The url of the issue to create or update the comment in
    :param comment_url: The url of the comment to update
    :param body: The new comment body
    :param only_if_exists: Only update an existing comment - don't create it
    """

    if comment_url is None:
        if only_if_exists:
            debug('Comment doesn\'t already exist - not creating it')
            return None
        # Create a new comment
        debug('Creating comment')
        response = github.post(issue_url, json={'body': body})
    else:
        # Update existing comment
        debug('Updating existing comment')
        response = github.patch(comment_url, json={'body': body})

    debug(body)
    debug(response.content.decode())
    response.raise_for_status()
    return cast(CommentUrl, response.json()['url'])


def find_issue_url(pr_url: str) -> IssueUrl:
    pr_hash = hashlib.sha256(pr_url.encode()).hexdigest()

    def get():
        response = github.get(pr_url)
        response.raise_for_status()
        return cast(IssueUrl, response.json()['_links']['issue']['href'] + '/comments')

    issue_url = job_cache.get_default_func(f'issue-href-cache/{pr_hash}', get)
    debug(f'discovered issue_url: {issue_url}')
    return cast(IssueUrl, issue_url)


def find_comment(issue_url: IssueUrl, username: str, action_inputs: PlanPrInputs) -> Tuple[Optional[CommentUrl], Optional[Plan]]:
    debug('Looking for an existing comment:')

    plan_id = plan_identifier(action_inputs)

    for comment in github.paged_get(issue_url):
        debug(json.dumps(comment))
        if comment['user']['login'] == username:
            match = re.match(rf'{re.escape(plan_id)}.*```(?:hcl)?(.*?)```.*', comment['body'], re.DOTALL)

            if match:
                return comment['url'], cast(Plan, match.group(1).strip())

    return None, None


def main() -> None:
    if len(sys.argv) < 2:
        sys.stdout.write(f'''Usage:
    STATUS="<status>" {sys.argv[0]} plan <plan.txt
    STATUS="<status>" {sys.argv[0]} status
    {sys.argv[0]} get >plan.txt
''')

    debug(repr(sys.argv))

    action_inputs = cast(PlanPrInputs, os.environ)

    try:
        collapse_threshold = int(os.environ['TF_PLAN_COLLAPSE_LENGTH'])
    except (ValueError, KeyError):
        collapse_threshold = 10

    pr_url = step_cache.get_default_func('pr_url', lambda: find_pr(github, env))
    issue_url = step_cache.get_default_func('issue_url', lambda: find_issue_url(pr_url))

    # Username is cached in the job tmp dir
    username = current_user(env)

    if 'comment_url' in step_cache and 'plan' in step_cache:
        comment_url = step_cache['comment_url']
        plan = step_cache['plan']
        debug(f'comment_url from step cache: {comment_url}')
        debug(f'plan from step cache: {plan}')
    else:
        comment_url, plan = find_comment(issue_url, username, action_inputs)
        step_cache['comment_url'], step_cache['plan'] = comment_url, plan
        debug(f'discovered comment_url: {comment_url}')
        debug(f'discovered plan: {plan}')

    status = cast(Status, os.environ.get('STATUS', ''))

    only_if_exists = False

    if sys.argv[1] == 'plan':
        plan = cast(Plan, sys.stdin.read().strip())

        if action_inputs['INPUT_ADD_GITHUB_COMMENT'] == 'changes-only' and os.environ.get('TF_CHANGES', 'true') == 'false':
            only_if_exists = True

        body = format_body(action_inputs, plan, status, collapse_threshold)
        step_cache['comment_url'] = update_comment(issue_url, comment_url, body, only_if_exists)
        step_cache['plan'] = plan

    elif sys.argv[1] == 'status':
        if plan is None:
            sys.exit(1)
        else:
            body = format_body(action_inputs, plan, status, collapse_threshold)
            step_cache['comment_url'] = update_comment(issue_url, comment_url, body, only_if_exists)

    elif sys.argv[1] == 'get':
        if plan is None:
            sys.exit(1)

        with open(sys.argv[2], 'w') as f:
            f.write(plan)


if __name__ == '__main__':
    main()
