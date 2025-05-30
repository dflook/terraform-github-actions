import hashlib
import json
import os
import subprocess
import re
import sys
from pathlib import Path
from typing import (NewType, Optional, cast, Tuple, List)

import canonicaljson

from github_actions.api import GithubApi, IssueUrl, PrUrl
from github_actions.cache import ActionsCache
from github_actions.commands import output
from github_actions.debug import debug
from github_actions.env import GithubEnv
from github_actions.find_pr import find_pr, WorkflowException
from github_actions.inputs import PlanPrInputs
from github_pr_comment.backend_config import complete_config, partial_config
from github_pr_comment.backend_fingerprint import fingerprint
from github_pr_comment.cmp import plan_cmp, remove_warnings, remove_unchanged_attributes
from github_pr_comment.comment import find_comment, TerraformComment, update_comment, serialize, deserialize, hide_comment
from github_pr_comment.hash import comment_hash, plan_hash, plan_out_hash
from github_pr_comment.plan_formatting import format_diff
from plan_renderer.outputs import render_outputs
from plan_renderer.variables import render_argument_list, Sensitive
from terraform.module import load_module, get_sensitive_variables
from terraform import hcl

Plan = NewType('Plan', str)
Status = NewType('Status', str)

job_cache = ActionsCache(Path(os.environ.get('JOB_TMP_DIR', '.')), 'job_cache')
step_cache = ActionsCache(Path(os.environ.get('STEP_TMP_DIR', '.')), 'step_cache')

env = cast(GithubEnv, os.environ)
github_token = env['TERRAFORM_ACTIONS_GITHUB_TOKEN']
github = GithubApi(env.get('GITHUB_API_URL', 'https://api.github.com'), github_token, os.environ.get('JOB_TMP_DIR', '.'))

ToolProductName = os.environ.get('TOOL_PRODUCT_NAME', 'Terraform')

def job_markdown_ref() -> str:
    return f'[{os.environ["GITHUB_WORKFLOW"]} #{os.environ["GITHUB_RUN_NUMBER"]}]({os.environ["GITHUB_SERVER_URL"]}/{os.environ["GITHUB_REPOSITORY"]}/actions/runs/{os.environ["GITHUB_RUN_ID"]})'

def job_workflow_ref() -> str:
    return f'Job {os.environ["GITHUB_WORKFLOW"]} #{os.environ["GITHUB_RUN_NUMBER"]} at {os.environ["GITHUB_SERVER_URL"]}/{os.environ["GITHUB_REPOSITORY"]}/actions/runs/{os.environ["GITHUB_RUN_ID"]}'

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

def format_description(action_inputs: PlanPrInputs, sensitive_variables: List[str]) -> str:

    mode = ''
    if action_inputs["INPUT_DESTROY"] == 'true':
        mode = '\n:bomb: Planning to destroy all resources'

    if action_inputs["INPUT_REFRESH"] == 'false':
        mode = '\n:recycle: Skipping refresh of resource state'

    if action_inputs['INPUT_LABEL']:
        return f'{ToolProductName} plan for __{action_inputs["INPUT_LABEL"]}__' + mode

    label = f'{ToolProductName} plan in __{action_inputs["INPUT_PATH"]}__'

    if action_inputs["INPUT_WORKSPACE"] != 'default':
        label += f' in the __{action_inputs["INPUT_WORKSPACE"]}__ workspace'

    label += mode

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

    if action_inputs["INPUT_VAR_FILE"]:
        label += f'\nWith var files: `{action_inputs["INPUT_VAR_FILE"]}`'

    if action_inputs["INPUT_VARIABLES"]:
        variables = hcl.loads(action_inputs["INPUT_VARIABLES"])

        # mark sensitive variables
        variables = {name: Sensitive() if name in sensitive_variables else value for name, value in variables.items()}

        stripped_vars = render_argument_list(variables).strip()
        if '\n' in stripped_vars:
            label += f'''<details open><summary>With variables</summary>

```hcl
{stripped_vars}
```
</details>
'''
        else:
            label += f'\nWith variables: `{stripped_vars}`'

    return label

def create_summary(plan: Plan, changes: bool=True) -> Optional[str]:
    summary = None

    to_move = 0

    for line in plan.splitlines():
        if line.startswith('No changes') or line.startswith('Error'):
            return line

        if re.match(r'  # \S+ has moved to \S+$', line):
            to_move += 1

        if line.startswith('Plan:'):
            summary = line

            if to_move and 'move' not in summary:
                summary = summary.rstrip('.') + f', {to_move} to move.'

        if line.startswith('Changes to Outputs'):
            if summary:
                return summary + ' Changes to Outputs.'
            else:
                return 'Changes to Outputs.'

    if summary:
        return summary

    # Terraform 1.4.0 starting forgetting to print the plan summary
    return 'Plan generated.' if changes else 'No changes.'


def current_user(actions_env: GithubEnv) -> str:
    token_hash = hashlib.sha256(f'dflook/terraform-github-actions/{github_token}'.encode()).hexdigest()
    cache_key = f'token-cache/{token_hash}'

    def graphql() -> Optional[str]:
        graphql_url = actions_env.get('GITHUB_GRAPHQL_URL', f'{actions_env["GITHUB_API_URL"]}/graphql')

        response = github.post(graphql_url, json={
            'query': "query { viewer { login } }"
        })
        debug(f'graphql response: {response.content}')

        if response.ok:
            try:
                return response.json()['data']['viewer']['login']
            except Exception:
                pass

        debug('Failed to get current user from graphql')

    def rest() -> Optional[str]:
        response = github.get(f'{actions_env["GITHUB_API_URL"]}/user')
        debug(f'rest response: {response.content}')

        if response.ok:
            user = response.json()

            return user['login']

    if cache_key in job_cache:
        username = job_cache[cache_key]
    else:

        # Not all tokens can be used with graphql
        # There is also no rest endpoint that can get the current login for app tokens :(
        # Try graphql first, then fallback to rest (e.g. for fine grained PATs)

        username = graphql() or rest()

        if username is None:
            debug('Unable to get username for the github token')
            username = 'github-actions[bot]'

        job_cache[cache_key] = username

    debug(f'token username is {username}')
    return username


def get_issue_url(pr_url: str) -> IssueUrl:
    pr_hash = hashlib.sha256(pr_url.encode()).hexdigest()
    cache_key = f'issue-url/{pr_hash}'

    if cache_key in job_cache:
        issue_url = job_cache[cache_key]
    else:
        response = github.get(pr_url)
        response.raise_for_status()
        issue_url = response.json()['_links']['issue']['href']

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

def new_pr_comment(backend_fingerprint: bytes) -> TerraformComment:
    pr_url = get_pr()
    issue_url = get_issue_url(pr_url)

    headers = {
        'workspace': os.environ.get('INPUT_WORKSPACE', 'default'),
    }

    if backend_type := os.environ.get('TERRAFORM_BACKEND_TYPE'):
        if backend_type == 'cloud':
            backend_type = 'remote'
        headers['backend_type'] = backend_type

    headers['label'] = os.environ.get('INPUT_LABEL') or None

    plan_modifier = {}
    if target := os.environ.get('INPUT_TARGET'):
        plan_modifier['target'] = sorted(t.strip() for t in target.replace(',', '\n', ).split('\n') if t.strip())

    if replace := os.environ.get('INPUT_REPLACE'):
        plan_modifier['replace'] = sorted(t.strip() for t in replace.replace(',', '\n', ).split('\n') if t.strip())

    if os.environ.get('INPUT_DESTROY') == 'true':
        plan_modifier['destroy'] = 'true'

    if plan_modifier:
        debug(f'Plan modifier: {plan_modifier}')
        headers['plan_modifier'] = hashlib.sha256(canonicaljson.encode_canonical_json(plan_modifier)).hexdigest()

    headers['backend'] = comment_hash(backend_fingerprint, pr_url)

    return TerraformComment(
        issue_url=issue_url,
        comment_url=None,
        node_id=None,
        headers={k: v for k, v in headers.items() if v is not None},
        description='',
        summary='',
        body='',
        status=''
    )

def get_comment(action_inputs: PlanPrInputs, backend_fingerprint: bytes, backup_fingerprint: bytes) -> TerraformComment:
    if 'comment' in step_cache:
        return deserialize(step_cache['comment'])

    pr_url = get_pr()
    issue_url = get_issue_url(pr_url)
    username = current_user(env)

    legacy_description = format_classic_description(action_inputs)

    headers = {
        'workspace': os.environ.get('INPUT_WORKSPACE', 'default'),
        'closed': None
    }

    if backend_type := os.environ.get('TERRAFORM_BACKEND_TYPE'):
        if backend_type == 'cloud':
            backend_type = 'remote'
        headers['backend_type'] = backend_type

    headers['label'] = os.environ.get('INPUT_LABEL') or None

    plan_modifier = {}
    if target := os.environ.get('INPUT_TARGET'):
        plan_modifier['target'] = sorted(t.strip() for t in target.replace(',', '\n', ).split('\n') if t.strip())

    if replace := os.environ.get('INPUT_REPLACE'):
        plan_modifier['replace'] = sorted(t.strip() for t in replace.replace(',', '\n', ).split('\n') if t.strip())

    if os.environ.get('INPUT_DESTROY') == 'true':
        plan_modifier['destroy'] = 'true'

    if plan_modifier:
        debug(f'Plan modifier: {plan_modifier}')
        headers['plan_modifier'] = hashlib.sha256(canonicaljson.encode_canonical_json(plan_modifier)).hexdigest()

    backup_headers = headers.copy()

    headers['backend'] = comment_hash(backend_fingerprint, pr_url)
    backup_headers['backend'] = comment_hash(backup_fingerprint, pr_url)

    return find_comment(github, issue_url, username, headers, backup_headers, legacy_description)

def is_approved(proposed_plan: str, comment: TerraformComment) -> bool:

    if approved_plan_hash := comment.headers.get('plan_hash'):
        debug('Approving plan based on plan hash')
        return plan_hash(proposed_plan, comment.issue_url) == approved_plan_hash
    else:
        debug('Approving plan based on plan text')
        return plan_cmp(proposed_plan, comment.body)

def is_approved_binary_plan(plan_path: str, comment: TerraformComment) -> bool:
    return plan_out_hash(plan_path, comment.issue_url) == comment.headers['plan_out_hash']

def truncate(text: str, max_size: int, too_big_message: str) -> str:
    lines = []
    total_size = 0

    for line in text.splitlines():
        line_size = len(line.encode()) + 1  # + newline
        if total_size + line_size > max_size:
            lines.append(too_big_message)
            break

        lines.append(line)
        total_size += line_size

    return '\n'.join(lines)

def format_plan_text(plan_text: str, format_type: str) -> Tuple[str, str]:
    """
    Format the given plan for insertion into a PR comment
    """

    max_body_size = 50000  # bytes

    if format_type == 'diff':
        plan_text = format_diff(plan_text)
        if len(plan_text.encode()) > max_body_size:
            # needs truncation
            return 'diff-trunc', truncate(plan_text, max_body_size, 'Plan is too large to fit in a PR comment. See the full plan in the workflow log.')
        else:
            return 'diff', plan_text
    else:
        if len(plan_text.encode()) > max_body_size:
            # needs truncation
            return 'trunc', truncate(plan_text, max_body_size, 'Plan is too large to fit in a PR comment. See the full plan in the workflow log.')
        else:
            return 'text', plan_text

def format_output_status(status: str, outputs: Optional[dict], remaining_size: int) -> str:

    stripped_output = render_outputs(outputs).strip()

    if stripped_output:
        if len(stripped_output) > remaining_size:
            stripped_output = truncate(stripped_output, remaining_size, 'Outputs are too large to fit in a PR comment. See the full outputs in the workflow log.')

        open_att = ' open' if len(stripped_output.splitlines()) < 6 else ''

        status += f'''\n<details{open_att}><summary>Outputs</summary>

```hcl
{stripped_output}
```
</details>
'''

    return status

def read_outputs(path: str) -> Optional[dict]:
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        debug(f'Failed to read terraform outputs from {path}')
        debug(str(e))
        return None

def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write(f'''Usage:
    STATUS="<status>" {sys.argv[0]} plan <plan.txt
    STATUS="<status>" {sys.argv[0]} status
    {sys.argv[0]} begin-apply
    {sys.argv[0]} error
    {sys.argv[0]} apply-complete <OUTPUTS_JSON_FILE>
    {sys.argv[0]} get <PLAN_TEXT_FILE>
    {sys.argv[0]} approved <PLAN_TEXT_FILE>
''')
        return 1

    debug(repr(sys.argv))

    action_inputs = cast(PlanPrInputs, os.environ)

    module = load_module(Path(action_inputs.get('INPUT_PATH', '.')))

    backend_type, backend_config = partial_config(action_inputs, module)
    partial_backend_fingerprint = fingerprint(backend_type, backend_config, os.environ)

    backend_type, backend_config = complete_config(action_inputs, module)
    backend_fingerprint = fingerprint(backend_type, backend_config, os.environ)

    comment = get_comment(action_inputs, backend_fingerprint, partial_backend_fingerprint)

    status = cast(Status, os.environ.get('STATUS', ''))

    if sys.argv[1] == 'plan':
        body = cast(Plan, sys.stdin.read().strip())
        description = format_description(action_inputs, get_sensitive_variables(module))

        only_if_exists = False
        if action_inputs['INPUT_ADD_GITHUB_COMMENT'] == 'changes-only' and os.environ.get('TF_CHANGES', 'true') == 'false':
            only_if_exists = True

        if action_inputs['INPUT_ADD_GITHUB_COMMENT'] == 'always-new' and comment.comment_url is not None:
            # Close the existing comment
            debug('Closing existing comment')
            update_comment(
                github,
                comment,
                summary=f'<strike>{comment.summary}</strike>',
                headers=comment.headers | {'closed': True},
                status=':spider_web: Plan is outdated'
            )
            hide_comment(
                github,
                comment,
                'OUTDATED'
            )

            # Create the replacement comment
            comment = new_pr_comment(backend_fingerprint)

        if comment.comment_url is None and only_if_exists:
            debug('Comment doesn\'t already exist - not creating it')
            return 0

        headers = comment.headers.copy()
        headers['plan_job_ref'] = job_workflow_ref()

        if os.environ.get('PLAN_OUT', ''):
            headers['plan_out_hash'] = plan_out_hash(os.environ['PLAN_OUT'], comment.issue_url)
        elif 'plan_out_hash' in headers:
            del headers['plan_out_hash']

        headers['plan_hash'] = plan_hash(body, comment.issue_url)
        format_type = os.environ.get('TF_ACTIONS_PLAN_FORMAT', 'diff')
        headers['plan_text_format'], plan_text = format_plan_text(body, format_type)

        changes = os.environ.get('TF_CHANGES') == 'true'

        highlighting = ''
        if os.environ.get('TF_CHANGES', 'true') == 'true':
            highlighting = 'diff' if format_type.startswith('diff') else 'hcl'

        comment = update_comment(
            github,
            comment,
            description=description,
            summary=create_summary(body, changes),
            headers=headers,
            body=plan_text,
            body_highlighting=highlighting,
            status=status
        )

    elif sys.argv[1] == 'status':
        if comment.comment_url is None:
            debug("Can't set status of comment that doesn't exist")
            return 1
        else:
            comment = update_comment(github, comment, status=status)

    elif sys.argv[1] == 'begin-apply':
        if comment.comment_url is None:
            debug("Can't set status of comment that doesn't exist")
            return 1
        else:
            comment = update_comment(github, comment, status=f':orange_circle: Applying plan in {job_markdown_ref()}')

    elif sys.argv[1] == 'error':
        if comment.comment_url is None:
            debug("Can't set status of comment that doesn't exist")
            return 1
        else:
            comment = update_comment(github, comment, headers=comment.headers | {'closed': True}, status=f':x: Error applying plan in {job_markdown_ref()}')

    elif sys.argv[1] == 'apply-complete':
        if comment.comment_url is None:
            debug("Can't set status of comment that doesn't exist")
            return 1
        else:
            outputs = read_outputs(sys.argv[2])

            remaining_size = 55000 - len(comment.body)

            comment = update_comment(github, comment, headers=comment.headers | {'closed': True}, status=format_output_status(f':white_check_mark: Plan applied in {job_markdown_ref()}', outputs, remaining_size))

    elif sys.argv[1] == 'cloud-no-changes-to-apply':
        if comment.comment_url is None:
            debug("Can't set status of comment that doesn't exist")
            return 1
        else:
            outputs = read_outputs(sys.argv[2])

            remaining_size = 55000 - len(comment.body)

            comment = update_comment(github, comment, headers=comment.headers | {'closed': True}, status=format_output_status(f':white_check_mark: No changes to apply in {job_markdown_ref()}', outputs, remaining_size))

    elif sys.argv[1] == 'get':
        if comment.comment_url is None:
            debug("Can't get the plan from comment that doesn't exist")
            return 1

        with open(sys.argv[2], 'w') as f:
            f.write(comment.body)

    elif sys.argv[1] == 'approved-binary':

        if comment.comment_url is None:
            sys.stdout.write("Plan not found on PR\n")
            sys.stdout.write("Generate the plan first using the dflook/terraform-plan action. Alternatively set the auto_approve input to 'true'\n")
            sys.stdout.write("If dflook/terraform-plan was used with add_github_comment set to changes-only, this may mean the plan has since changed to include changes\n")
            output('failure-reason', 'plan-changed')
            sys.exit(1)

        if not is_approved_binary_plan(sys.argv[2], comment):

            sys.stdout.write("Not applying the plan - it has changed from the plan on the PR\n")
            sys.stdout.write("The plan on the PR must be up to date. Alternatively, set the auto_approve input to 'true' to apply outdated plans\n")
            comment = update_comment(github, comment, status=f':x: Plan not applied in {job_markdown_ref()} (Plan has changed)')

            if plan_ref := comment.headers.get('plan_job_ref'):
                sys.stdout.write(f'\nThis plan is different to the plan generated by the dflook/terraform-plan action in {plan_ref}\n')

            output('failure-reason', 'plan-changed')

            step_cache['comment'] = serialize(comment)
            return 1

    elif sys.argv[1] == 'approved':

        proposed_plan = remove_warnings(remove_unchanged_attributes(Path(sys.argv[2]).read_text().strip()))
        if comment.comment_url is None:
            sys.stdout.write("Plan not found on PR\n")
            sys.stdout.write("Generate the plan first using the dflook/terraform-plan action. Alternatively set the auto_approve input to 'true'\n")
            sys.stdout.write("If dflook/terraform-plan was used with add_github_comment set to changes-only, this may mean the plan has since changed to include changes\n")
            output('failure-reason', 'plan-changed')
            sys.exit(1)

        if not is_approved(proposed_plan, comment):

            sys.stdout.write("Not applying the plan - it has changed from the plan on the PR\n")
            sys.stdout.write("The plan on the PR must be up to date. Alternatively, set the auto_approve input to 'true' to apply outdated plans\n")
            comment = update_comment(github, comment, status=f':x: Plan not applied in {job_markdown_ref()} (Plan has changed)')

            approved_plan_path = os.path.join(os.environ['STEP_TMP_DIR'], 'approved-plan.txt')
            with open(approved_plan_path, 'w') as f:
                f.write(comment.body.strip())

            proposed_plan_path = os.path.join(os.environ['STEP_TMP_DIR'], 'proposed-plan.txt')
            with open(proposed_plan_path, 'w') as f:
                format_type = 'diff' if comment.headers.get('plan_text_format', 'text') == 'diff' else 'text'
                _, formatted_proposed_plan = format_plan_text(proposed_plan.strip(), format_type)
                f.write(formatted_proposed_plan.strip())

            debug(f'diff {proposed_plan_path} {approved_plan_path}')
            diff_complete = subprocess.run(['diff', proposed_plan_path, approved_plan_path], check=False, capture_output=True, encoding='utf-8')

            if diff_complete.returncode != 0:
                sys.stdout.write("""Performing diff between the pull request plan and the plan generated at execution time.
> are lines from the plan in the pull request
< are lines from the plan generated at execution
Plan differences:
""")

            sys.stdout.write(diff_complete.stdout)
            sys.stderr.write(diff_complete.stderr)

            if comment.headers.get('plan_text_format', 'text').endswith('trunc'):
                sys.stdout.write('\nThe plan text was too large for a PR comment, not all differences may be shown here.')

            if plan_ref := comment.headers.get('plan_job_ref'):
                sys.stdout.write(f'\nCompare with the plan generated by the dflook/terraform-plan action in {plan_ref}\n')

            output('failure-reason', 'plan-changed')

            step_cache['comment'] = serialize(comment)
            return 1

    step_cache['comment'] = serialize(comment)
    return 0

if __name__ == '__main__':
    sys.exit(main())
