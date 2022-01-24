#!/usr/bin/python3

import datetime
import hashlib
import json
import os
import re
import sys
from typing import (Any, Dict, Iterable, NewType, Optional, Tuple, TypedDict,
                    cast)

import requests

GitHubUrl = NewType('GitHubUrl', str)
PrUrl = NewType('PrUrl', GitHubUrl)
IssueUrl = NewType('IssueUrl', GitHubUrl)
CommentUrl = NewType('CommentUrl', GitHubUrl)
Plan = NewType('Plan', str)
Status = NewType('Status', str)


class GitHubActionsEnv(TypedDict):
    """
    Environment variables that are set by the actions runner
    """
    GITHUB_API_URL: str
    GITHUB_TOKEN: str
    GITHUB_EVENT_PATH: str
    GITHUB_EVENT_NAME: str
    GITHUB_REPOSITORY: str
    GITHUB_SHA: str
    GITHUB_REF_TYPE: str
    GITHUB_REF: str


job_tmp_dir = os.environ.get('JOB_TMP_DIR', '.')
step_tmp_dir = os.environ.get('STEP_TMP_DIR', '.')

env = cast(GitHubActionsEnv, os.environ)


def github_session(github_env: GitHubActionsEnv) -> requests.Session:
    """
    A request session that is configured for the github API
    """
    session = requests.Session()
    session.headers['authorization'] = f'token {github_env["GITHUB_TOKEN"]}'
    session.headers['user-agent'] = 'terraform-github-actions'
    session.headers['accept'] = 'application/vnd.github.v3+json'
    return session


github = github_session(env)


class ActionInputs(TypedDict):
    """
    Actions input environment variables that are set by the runner
    """
    INPUT_BACKEND_CONFIG: str
    INPUT_BACKEND_CONFIG_FILE: str
    INPUT_VARIABLES: str
    INPUT_VAR: str
    INPUT_VAR_FILE: str
    INPUT_PATH: str
    INPUT_WORKSPACE: str
    INPUT_LABEL: str
    INPUT_ADD_GITHUB_COMMENT: str
    INPUT_TARGET: str
    INPUT_REPLACE: str

class WorkflowException(Exception):
    """An exception that should result in an error in the workflow log"""

def plan_identifier(action_inputs: ActionInputs) -> str:
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


def github_api_request(method: str, *args, **kwargs) -> requests.Response:
    response = github.request(method, *args, **kwargs)

    if 400 <= response.status_code < 500:
        debug(str(response.headers))

        try:
            message = response.json()['message']

            if response.headers['X-RateLimit-Remaining'] == '0':
                limit_reset = datetime.datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))
                sys.stdout.write(message)
                sys.stdout.write(f' Try again when the rate limit resets at {limit_reset} UTC.\n')
                sys.exit(1)

            if message != 'Resource not accessible by integration':
                sys.stdout.write(message)
                sys.stdout.write('\n')
                debug(response.content.decode())

        except Exception:
            sys.stdout.write(response.content.decode())
            sys.stdout.write('\n')
            raise

    return response


def debug(msg: str) -> None:
    sys.stderr.write(msg)
    sys.stderr.write('\n')


def paginate(url: GitHubUrl, *args, **kwargs) -> Iterable[Dict[str, Any]]:
    while True:
        response = github_api_request('get', url, *args, **kwargs)
        response.raise_for_status()

        yield from response.json()

        if 'next' in response.links:
            url = response.links['next']['url']
        else:
            return


def find_pr(actions_env: GitHubActionsEnv) -> PrUrl:
    """
    Find the pull request this event is related to

    >>> find_pr()
    'https://api.github.com/repos/dflook/terraform-github-actions/pulls/8'

    """

    event: Optional[Dict[str, Any]]

    if os.path.isfile(actions_env['GITHUB_EVENT_PATH']):
        with open(actions_env['GITHUB_EVENT_PATH']) as f:
            event = json.load(f)
    else:
        debug('Event payload is not available')
        event = None

    event_type = actions_env['GITHUB_EVENT_NAME']

    if event_type in ['pull_request', 'pull_request_review_comment', 'pull_request_target', 'pull_request_review', 'issue_comment']:

        if event is not None:
            # Pull pr url from event payload

            if event_type in ['pull_request', 'pull_request_review_comment', 'pull_request_target', 'pull_request_review']:
                return cast(PrUrl, event['pull_request']['url'])

            if event_type == 'issue_comment':

                if 'pull_request' in event['issue']:
                    return cast(PrUrl, event['issue']['pull_request']['url'])
                else:
                    raise WorkflowException('This comment is not for a PR. Add a filter of `if: github.event.issue.pull_request`')

        else:
            # Event payload is not available

            if actions_env.get('GITHUB_REF_TYPE') == 'branch':
                if match := re.match(r'refs/pull/(\d+)/', actions_env.get('GITHUB_REF', '')):
                    return cast(PrUrl, f'{actions_env["GITHUB_API_URL"]}/repos/{actions_env["GITHUB_REPOSITORY"]}/pulls/{match.group(1)}')

            raise WorkflowException(f'Event payload is not available at the GITHUB_EVENT_PATH {actions_env["GITHUB_EVENT_PATH"]!r}. ' +
                            f'This is required when run by {event_type} events. The environment has not been setup properly by the actions runner. ' +
                            'This can happen when the runner is running in a container')

    elif event_type == 'push':
        repo = actions_env['GITHUB_REPOSITORY']
        commit = actions_env['GITHUB_SHA']

        def prs() -> Iterable[Dict[str, Any]]:
            url = f'{actions_env["GITHUB_API_URL"]}/repos/{repo}/pulls'
            yield from paginate(cast(PrUrl, url), params={'state': 'all'})

        for pr in prs():
            if pr['merge_commit_sha'] == commit:
                return cast(PrUrl, pr['url'])

        raise WorkflowException(f'No PR found in {repo} for commit {commit} (was it pushed directly to the target branch?)')

    else:
        raise WorkflowException(f"The {event_type} event doesn\'t relate to a Pull Request.")


def current_user(actions_env: GitHubActionsEnv) -> str:
    token_hash = hashlib.sha256(actions_env['GITHUB_TOKEN'].encode()).hexdigest()

    try:
        with open(os.path.join(job_tmp_dir, 'token-cache', token_hash)) as f:
            username = f.read()
            debug(f'GITHUB_TOKEN username from token-cache: {username}')
            return username
    except Exception as e:
        debug(str(e))

    response = github_api_request('get', f'{actions_env["GITHUB_API_URL"]}/user')
    if response.status_code != 403:
        user = response.json()
        debug(json.dumps(user))

        username = user['login']
    else:
        # Assume this is the github actions app token
        username = 'github-actions[bot]'

    try:
        os.makedirs(os.path.join(job_tmp_dir, 'token-cache'), exist_ok=True)
        with open(os.path.join(job_tmp_dir, 'token-cache', token_hash), 'w') as f:
            f.write(username)
    except Exception as e:
        debug(str(e))

    debug(f'discovered GITHUB_TOKEN username: {username}')
    return username


def create_summary(plan) -> Optional[str]:
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


def format_body(action_inputs: ActionInputs, plan: Plan, status: Status, collapse_threshold: int) -> str:

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
{ f'<summary>{summary_line}</summary>' if summary_line is not None else '' }

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
        response = github_api_request('post', issue_url, json={'body': body})
    else:
        # Update existing comment
        debug('Updating existing comment')
        response = github_api_request('patch', comment_url, json={'body': body})

    debug(body)
    debug(response.content.decode())
    response.raise_for_status()
    return cast(CommentUrl, response.json()['url'])


def find_issue_url(pr_url: str) -> IssueUrl:
    pr_hash = hashlib.sha256(pr_url.encode()).hexdigest()

    try:
        with open(os.path.join(job_tmp_dir, 'issue-href-cache', pr_hash)) as f:
            issue_url = f.read()
            debug(f'issue_url from issue-href-cache: {issue_url}')
            return cast(IssueUrl, issue_url)
    except Exception as e:
        debug(str(e))

    response = github_api_request('get', pr_url)
    response.raise_for_status()

    issue_url = cast(IssueUrl, response.json()['_links']['issue']['href'] + '/comments')

    try:
        os.makedirs(os.path.join(job_tmp_dir, 'issue-href-cache'), exist_ok=True)
        with open(os.path.join(job_tmp_dir, 'issue-href-cache', pr_hash), 'w') as f:
            f.write(issue_url)
    except Exception as e:
        debug(str(e))

    debug(f'discovered issue_url: {issue_url}')
    return cast(IssueUrl, issue_url)


def find_comment(issue_url: IssueUrl, username: str, action_inputs: ActionInputs) -> Tuple[Optional[CommentUrl], Optional[Plan]]:
    debug('Looking for an existing comment:')

    plan_id = plan_identifier(action_inputs)

    for comment in paginate(issue_url):
        debug(json.dumps(comment))
        if comment['user']['login'] == username:
            match = re.match(rf'{re.escape(plan_id)}.*```(?:hcl)?(.*?)```.*', comment['body'], re.DOTALL)

            if match:
                return comment['url'], cast(Plan, match.group(1).strip())

    return None, None

def read_step_cache() -> Dict[str, str]:
    try:
        with open(os.path.join(step_tmp_dir, 'github_pr_comment.cache')) as f:
            debug('step cache loaded')
            return json.load(f)
    except Exception as e:
        debug(str(e))
        return {}

def save_step_cache(**kwargs) -> None:
    try:
        with open(os.path.join(step_tmp_dir, 'github_pr_comment.cache'), 'w') as f:
            json.dump(kwargs, f)
            debug('step cache saved')
    except Exception as e:
        debug(str(e))

def main() -> None:
    if len(sys.argv) < 2:
        sys.stdout.write(f'''Usage:
    STATUS="<status>" {sys.argv[0]} plan <plan.txt
    STATUS="<status>" {sys.argv[0]} status
    {sys.argv[0]} get >plan.txt
''')

    debug(repr(sys.argv))

    action_inputs = cast(ActionInputs, os.environ)

    try:
        collapse_threshold = int(os.environ['TF_PLAN_COLLAPSE_LENGTH'])
    except (ValueError, KeyError):
        collapse_threshold = 10

    step_cache = read_step_cache()

    if step_cache.get('pr_url') is not None:
        pr_url = step_cache['pr_url']
        debug(f'pr_url from step cache: {pr_url}')
    else:
        try:
            pr_url = find_pr(env)
        except WorkflowException as e:
            sys.stdout.write('\n' + str(e) + '\n')
            sys.exit(1)
        debug(f'discovered pr_url: {pr_url}')

    if step_cache.get('pr_url') == pr_url and step_cache.get('issue_url') is not None:
        issue_url = step_cache['issue_url']
        debug(f'issue_url from step cache: {issue_url}')
    else:
        issue_url = find_issue_url(pr_url)

    # Username is cached in the job tmp dir
    username = current_user(env)

    if step_cache.get('comment_url') is not None and step_cache.get('plan') is not None:
        comment_url = step_cache['comment_url']
        plan = step_cache['plan']
        debug(f'comment_url from step cache: {comment_url}')
        debug(f'plan from step cache: {plan}')
    else:
        comment_url, plan = find_comment(issue_url, username, action_inputs)
        debug(f'discovered comment_url: {comment_url}')
        debug(f'discovered plan: {plan}')

    status = cast(Status, os.environ.get('STATUS', ''))

    only_if_exists = False

    if sys.argv[1] == 'plan':
        plan = cast(Plan, sys.stdin.read().strip())

        if action_inputs['INPUT_ADD_GITHUB_COMMENT'] == 'changes-only' and os.environ.get('TF_CHANGES', 'true') == 'false':
            only_if_exists = True

        body = format_body(action_inputs, plan, status, collapse_threshold)
        comment_url = update_comment(issue_url, comment_url, body, only_if_exists)

    elif sys.argv[1] == 'status':
        if plan is None:
            sys.exit(1)
        else:
            body = format_body(action_inputs, plan, status, collapse_threshold)
            comment_url = update_comment(issue_url, comment_url, body, only_if_exists)

    elif sys.argv[1] == 'get':
        if plan is None:
            sys.exit(1)

        with open(sys.argv[2], 'w') as f:
            f.write(plan)

    save_step_cache(pr_url=pr_url, issue_url=issue_url, comment_url=comment_url, plan=plan)

if __name__ == '__main__':
    main()
