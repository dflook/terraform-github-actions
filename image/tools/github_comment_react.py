#!/usr/bin/python3

import datetime
import json
import os
import sys
from typing import NewType, Optional, TypedDict, cast

import requests

GitHubUrl = NewType('GitHubUrl', str)
CommentReactionUrl = NewType('CommentReactionUrl', GitHubUrl)


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
    TERRAFORM_ACTIONS_GITHUB_TOKEN: str


job_tmp_dir = os.environ.get('JOB_TMP_DIR', '.')
step_tmp_dir = os.environ.get('STEP_TMP_DIR', '.')

env = cast(GitHubActionsEnv, os.environ)


def github_session(github_env: GitHubActionsEnv) -> requests.Session:
    """
    A request session that is configured for the github API
    """
    session = requests.Session()
    session.headers['authorization'] = f'token {github_env["TERRAFORM_ACTIONS_GITHUB_TOKEN"]}'
    session.headers['user-agent'] = 'terraform-github-actions'
    session.headers['accept'] = 'application/vnd.github.v3+json'
    return session


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


def find_reaction_url(actions_env: GitHubActionsEnv) -> Optional[CommentReactionUrl]:
    event_type = actions_env['GITHUB_EVENT_NAME']

    if event_type not in ['issue_comment', 'pull_request_review_comment']:
        return None

    try:
        with open(actions_env['GITHUB_EVENT_PATH']) as f:
            event = json.load(f)

        return event['comment']['reactions']['url']
    except Exception as e:
        debug(str(e))

    return None


def react(comment_reaction_url: CommentReactionUrl, reaction_type: str) -> None:
    github_api_request('post', comment_reaction_url, json={'content': reaction_type})


def main() -> None:
    if len(sys.argv) < 2:
        print(f'''Usage:
    {sys.argv[0]} <reaction type>''')

    debug(repr(sys.argv))

    reaction_url = find_reaction_url(env)
    if reaction_url is not None:
        react(reaction_url, sys.argv[1])


if __name__ == '__main__':
    if 'TERRAFORM_ACTIONS_GITHUB_TOKEN' not in env:
        exit(0)
    github = github_session(env)
    main()
