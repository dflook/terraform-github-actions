#!/usr/bin/python3

import json
import os
import re
import sys
import datetime
import hashlib
from typing import Optional, Dict, Iterable

import requests

github = requests.Session()
github.headers['authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
github.headers['user-agent'] = 'terraform-github-actions'
github.headers['accept'] = 'application/vnd.github.v3+json'

github_url = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
github_api_url = os.environ.get('GITHUB_API_URL', 'https://api.github.com')

def github_api_request(method, *args, **kwargs):
    response = github.request(method, *args, **kwargs)

    if 400 <= response.status_code < 500:
        debug(str(response.headers))

        try:
            message = response.json()['message']

            if response.headers['X-RateLimit-Remaining'] == '0':
                limit_reset = datetime.datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))
                sys.stdout.write(message)
                sys.stdout.write(f' Try again when the rate limit resets at {limit_reset} UTC.\n')
                exit(1)

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

def paginate(url, *args, **kwargs) -> Iterable[Dict]:

    while True:
        response = github_api_request('get', url, *args, **kwargs)
        response.raise_for_status()

        yield from response.json()

        if 'next' in response.links:
            url = response.links['next']['url']
        else:
            return

def prs(repo: str) -> Iterable[Dict]:
    url = f'{github_api_url}/repos/{repo}/pulls'
    yield from paginate(url, params={'state': 'all'})


def find_pr() -> str:
    """
    Find the pull request this event is related to

    >>> find_pr()
    'https://api.github.com/repos/dflook/terraform-github-actions/pulls/8'

    """

    with open(os.environ['GITHUB_EVENT_PATH']) as f:
        event = json.load(f)

    event_type = os.environ['GITHUB_EVENT_NAME']

    if event_type in ['pull_request', 'pull_request_review_comment', 'pull_request_target', 'pull_request_review']:
        return event['pull_request']['url']

    elif event_type == 'issue_comment':

        if 'pull_request' in event['issue']:
            return event['issue']['pull_request']['url']
        else:
            raise Exception(f'This comment is not for a PR. Add a filter of `if: github.event.issue.pull_request`')

    elif event_type == 'push':
        repo = os.environ['GITHUB_REPOSITORY']
        commit = os.environ['GITHUB_SHA']

        for pr in prs(repo):
            if pr['merge_commit_sha'] == commit:
                return pr['url']

        raise Exception(f'No PR found in {repo} for commit {commit} (was it pushed directly to the target branch?)')

    else:
        raise Exception(f"The {event_type} event doesn\'t relate to a Pull Request.")

def current_user() -> str:

    token_hash = hashlib.sha256(os.environ["GITHUB_TOKEN"].encode()).hexdigest()

    try:
        with open(f'.dflook-terraform/token-cache/{token_hash}') as f:
            username = f.read()
            debug(f'GITHUB_TOKEN username: {username}')
            return username
    except Exception as e:
        debug(str(e))

    response = github_api_request('get', f'{github_api_url}/user')
    if response.status_code != 403:
        user = response.json()
        debug('GITHUB_TOKEN user:')
        debug(json.dumps(user))

        username = user['login']
    else:
        # Assume this is the github actions app token
        username = 'github-actions[bot]'

    try:
        os.makedirs('.dflook-terraform/token-cache', exist_ok=True)
        with open(f'.dflook-terraform/token-cache/{token_hash}', 'w') as f:
            f.write(username)
    except Exception as e:
        debug(str(e))

    debug(f'GITHUB_TOKEN username: {username}')
    return username

class TerraformComment:
    """
    The GitHub comment for this specific terraform plan
    """

    def __init__(self, pr_url: str=None):
        self._plan = None
        self._status = None
        self._comment_url = None

        if pr_url is None:
            return

        response = github_api_request('get', pr_url)
        response.raise_for_status()

        self._issue_url = response.json()['_links']['issue']['href'] + '/comments'

        username = current_user()

        debug('Looking for an existing comment:')

        for comment in paginate(self._issue_url):
            debug(json.dumps(comment))
            if comment['user']['login'] == username:
                match = re.match(rf'{re.escape(self._comment_identifier)}.*```(?:hcl)?(.*?)```.*', comment['body'], re.DOTALL)

                if not match:
                    match = re.match(rf'{re.escape(self._old_comment_identifier)}\n```(.*?)```.*', comment['body'], re.DOTALL)

                if match:
                    self._comment_url = comment['url']
                    self._plan = match.group(1).strip()
                    return

    @property
    def _comment_identifier(self):
        if self.label:
            return f'Terraform plan for __{self.label}__'

        label = f'Terraform plan in __{self.path}__'

        if self.workspace != 'default':
            label += f' in the __{self.workspace}__ workspace'

        if self.backend_config:
            label += f'\nWith backend config: `{self.backend_config}`'

        if self.backend_config_files:
            label += f'\nWith backend config files: `{self.backend_config_files}`'

        if self.vars:
            label += f'\nWith vars: `{self.vars}`'

        if self.var_files:
            label += f'\nWith var files: `{self.var_files}`'

        if self.variables:
            stripped_vars = self.variables.strip()
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

    @property
    def _old_comment_identifier(self):
        if self.label:
            return f'Terraform plan for __{self.label}__'

        label = f'Terraform plan in __{self.path}__'

        if self.workspace != 'default':
            label += f' in the __{self.workspace}__ workspace'

        if self.init_args:
            label += f'\nUsing init args: `{self.init_args}`'
        if self.plan_args:
            label += f'\nUsing plan args: `{self.plan_args}`'

        return label

    @property
    def backend_config(self) -> Optional[str]:
        if os.environ.get('INPUT_BACKEND_CONFIG') is None:
            return None

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

        for field in os.environ.get('INPUT_BACKEND_CONFIG', '').split(','):
            if not field:
                continue

            if not has_bad_word(field):
                clean.append(field)

        return ','.join(clean)

    @property
    def backend_config_files(self) -> str:
        return os.environ.get('INPUT_BACKEND_CONFIG_FILE')

    @property
    def variables(self) -> str:
        return os.environ.get('INPUT_VARIABLES')

    @property
    def vars(self) -> str:
        return os.environ.get('INPUT_VAR')

    @property
    def var_files(self) -> str:
        return os.environ.get('INPUT_VAR_FILE')

    @property
    def path(self) -> str:
        return os.environ['INPUT_PATH']

    @property
    def workspace(self) -> str:
        return os.environ.get('INPUT_WORKSPACE')

    @property
    def label(self) -> str:
        return os.environ.get('INPUT_LABEL')

    @property
    def init_args(self) -> str:
        return os.environ['INIT_ARGS']

    @property
    def plan_args(self) -> str:
        return os.environ['PLAN_ARGS']

    @property
    def plan(self) -> Optional[str]:
        return self._plan

    @plan.setter
    def plan(self, plan: str) -> None:
        self._plan = plan.strip()

    @property
    def status(self) -> Optional[str]:
        return self._status

    @status.setter
    def status(self, status: str) -> None:
        self._status = status.strip()

    def body(self) -> str:
        body = f'{self._comment_identifier}\n```hcl\n{self.plan}\n```'

        if self.status:
            body += '\n' + self.status

        return body

    def collapsable_body(self) -> str:

        try:
            collapse_threshold = int(os.environ['TF_PLAN_COLLAPSE_LENGTH'])
        except (ValueError, KeyError):
            collapse_threshold = 10

        open = ''
        highlighting = ''

        if self.plan.startswith('Error'):
            open = ' open'
        elif 'Plan:' in self.plan:
            highlighting = 'hcl'
            num_lines = len(self.plan.splitlines())
            if num_lines < collapse_threshold:
                open = ' open'

        body = f'''{self._comment_identifier}
<details{open}>
  <summary>{self.summary()}</summary>

```{highlighting}
{self.plan}
```
</details>
'''

        if self.status:
            body += '\n' + self.status

        return body

    def summary(self) -> str:
        summary = None

        for line in self.plan.splitlines():
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

    def update_comment(self, only_if_exists=False):
        body = self.collapsable_body()
        debug(body)

        if self._comment_url is None:
            if only_if_exists:
                debug('Comment doesn\'t already exist - not creating it')
                return
            # Create a new comment
            debug('Creating comment')
            response = github_api_request('post', self._issue_url, json={'body': body})
        else:
            # Update existing comment
            debug('Updating existing comment')
            response = github_api_request('patch', self._comment_url, json={'body': body})

        debug(response.content.decode())
        response.raise_for_status()
        self._comment_url = response.json()['url']


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'''Usage:
    STATUS="<status>" {sys.argv[0]} plan <plan.txt
    STATUS="<status>" {sys.argv[0]} status
    {sys.argv[0]} get >plan.txt''')

    tf_comment = TerraformComment(find_pr())
    only_if_exists = False

    if sys.argv[1] == 'plan':
        tf_comment.plan = sys.stdin.read().strip()
        tf_comment.status = os.environ['STATUS']

        if os.environ['INPUT_ADD_GITHUB_COMMENT'] == 'changes-only' and os.environ.get('TF_CHANGES', 'true') == 'false':
            only_if_exists = True

    elif sys.argv[1] == 'status':
        if tf_comment.plan is None:
            exit(1)
        else:
            tf_comment.status = os.environ['STATUS']
    elif sys.argv[1] == 'get':
        if tf_comment.plan is None:
            exit(1)

        with open(sys.argv[2], 'w') as f:
            f.write(tf_comment.plan)
        exit(0)

    tf_comment.update_comment(only_if_exists)
