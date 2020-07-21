#!/usr/bin/python3

import json
import os
import re
import sys
from typing import Optional, Dict, Iterable

import requests

github = requests.Session()
github.headers['authorization'] = f'Bearer {os.environ["GITHUB_TOKEN"]}'


def debug(msg: str) -> None:
    for line in msg.splitlines():
        sys.stderr.write(f'::debug::{line}\n')


def prs(repo: str) -> Iterable[Dict]:
    url = f'https://api.github.com/repos/{repo}/pulls'

    while True:
        response = github.get(url, params={'state': 'all'})
        response.raise_for_status()

        for pr in response.json():
            yield pr

        if 'next' in response.links:
            url = response.links['next']['url']
        else:
            return


def find_pr() -> str:
    if os.environ['GITHUB_EVENT_NAME'] == 'pull_request':
        with open(os.environ['GITHUB_EVENT_PATH']) as f:
            event = json.load(f)

        return event['pull_request']['url']

    repo = os.environ['GITHUB_REPOSITORY']
    commit = os.environ['GITHUB_SHA']

    for pr in prs(repo):
        if pr['merge_commit_sha'] == commit:
            return pr['url']

    raise Exception(f'No PR found in {repo} for commit {commit} (was it pushed directly to the target branch?)')


class TerraformComment:
    """
    The GitHub comment for this specific terraform plan
    """

    def __init__(self, pr_url: str):
        self._plan = None
        self._status = None

        response = github.get(pr_url)
        response.raise_for_status()

        self._issue_url = response.json()['_links']['issue']['href'] + '/comments'
        response = github.get(self._issue_url)
        response.raise_for_status()

        self._comment_url = None
        debug('Looking for an existing comment:')
        for comment in response.json():
            debug(json.dumps(comment))
            if comment['user']['login'] == 'github-actions[bot]':
                match = re.match(rf'{re.escape(self._comment_identifier)}\n```(.*?)```(.*)', comment['body'], re.DOTALL)

                if match:
                    self._comment_url = comment['url']
                    self._plan = match.group(1).strip()
                    self._status = match.group(2).strip()
                    return

    @property
    def _comment_identifier(self):
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

    def update_comment(self):
        body = f'{self._comment_identifier}\n```\n{self.plan}\n```'

        if self.status:
            body += '\n' + self.status

        debug(body)

        if self._comment_url is None:
            # Create a new comment
            debug('Creating comment')
            response = github.post(self._issue_url, json={'body': body})
        else:
            # Update existing comment
            debug('Updating existing comment')
            response = github.patch(self._comment_url, json={'body': body})

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

    if sys.argv[1] == 'plan':
        tf_comment.plan = sys.stdin.read().strip()
        tf_comment.status = os.environ['STATUS']
    elif sys.argv[1] == 'status':
        if tf_comment.plan is None:
            exit(1)
        else:
            tf_comment.status = os.environ['STATUS']
    elif sys.argv[1] == 'get':
        if tf_comment.plan is None:
            exit(1)
        print(tf_comment.plan)

    tf_comment.update_comment()
