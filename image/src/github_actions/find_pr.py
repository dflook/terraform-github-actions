import json
import os
import re
from typing import Optional, Any, cast, Iterable

from github_actions.api import PrUrl, GithubApi
from github_actions.debug import debug
from github_actions.env import GithubEnv


class WorkflowException(Exception):
    """An exception that should result in an error in the workflow log"""


def find_pr(github: GithubApi, actions_env: GithubEnv) -> PrUrl:
    """
    Find the pull request this event is related to

    >>> find_pr()
    'https://api.github.com/repos/dflook/terraform-github-actions/pulls/8'

    """

    event: Optional[dict[str, Any]]

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

    elif event_type == 'repository_dispatch':
        if 'pull_request' not in event['client_payload'] or not isinstance(event['client_payload']['pull_request'], dict):
            raise WorkflowException('The repository_dispatch event must have a pull_request object in the client_payload')
        if 'url' not in event['client_payload']['pull_request']:
            raise WorkflowException('The pull_request object in the client_payload must have a url')

        return cast(PrUrl, event['client_payload']['pull_request']['url'])

    elif event_type == 'push':
        repo = actions_env['GITHUB_REPOSITORY']
        commit = actions_env['GITHUB_SHA']

        def prs() -> Iterable[dict[str, Any]]:
            url = cast(PrUrl, f'{actions_env["GITHUB_API_URL"]}/repos/{repo}/pulls')
            yield from github.paged_get(url, params={'state': 'all'})

        for pr in prs():
            if pr['merge_commit_sha'] == commit:
                return cast(PrUrl, pr['url'])

        raise WorkflowException(f'No PR found in {repo} for commit {commit} (was it pushed directly to the target branch?)')

    raise WorkflowException(f"The {event_type} event doesn\'t relate to a Pull Request.")
