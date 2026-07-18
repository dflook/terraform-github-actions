import json

import pytest

from github_actions.find_pr import find_pr, WorkflowException


def env(event_path, api_url='https://api.github.com'):
    return {
        'GITHUB_EVENT_PATH': str(event_path),
        'GITHUB_EVENT_NAME': 'repository_dispatch',
        'GITHUB_API_URL': api_url,
    }


def write_event(tmp_path, payload):
    event_path = tmp_path / 'event.json'
    event_path.write_text(json.dumps(payload))
    return event_path


def test_repository_dispatch_missing_event_payload(tmp_path):
    # The event payload file may be missing on a broken actions runner
    with pytest.raises(WorkflowException):
        find_pr(None, env(tmp_path / 'nonexistent.json'))


@pytest.mark.parametrize('payload', [
    {},
    {'client_payload': None},
    {'client_payload': {}},
    {'client_payload': {'pull_request': None}},
    {'client_payload': {'pull_request': 'https://api.github.com/repos/dflook/test/pulls/1'}},
])
def test_repository_dispatch_missing_pull_request(tmp_path, payload):
    # client_payload is optional when creating a repository_dispatch event
    with pytest.raises(WorkflowException):
        find_pr(None, env(write_event(tmp_path, payload)))


@pytest.mark.parametrize('pull_request', [
    {},
    {'url': None},
    {'url': 5},
])
def test_repository_dispatch_missing_url(tmp_path, pull_request):
    with pytest.raises(WorkflowException):
        find_pr(None, env(write_event(tmp_path, {'client_payload': {'pull_request': pull_request}})))


def test_repository_dispatch_url_for_wrong_host(tmp_path):
    event_path = write_event(tmp_path, {'client_payload': {'pull_request': {'url': 'https://evil.example.com/repos/dflook/test/pulls/1'}}})

    with pytest.raises(WorkflowException):
        find_pr(None, env(event_path))


def test_repository_dispatch(tmp_path):
    url = 'https://api.github.com/repos/dflook/test/pulls/1'
    event_path = write_event(tmp_path, {'client_payload': {'pull_request': {'url': url}}})

    assert find_pr(None, env(event_path)) == url
