import json

import pytest
import requests

from github_actions.api import GithubApi

RELEASES_URL = 'https://api.github.com/repos/opentofu/opentofu/releases'

RATE_LIMIT_HEADERS = {
    'X-RateLimit-Remaining': '0',
    'X-RateLimit-Limit': '60',
    'X-RateLimit-Reset': '1789000000',
}


def fake_response(status=403, message='API rate limit exceeded for 1.2.3.4.', headers=None, url=RELEASES_URL):
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps({'message': message}).encode()
    response.headers.update(headers or {})

    request = requests.PreparedRequest()
    request.method = 'GET'
    request.url = url
    response.request = request

    return response


def github_api(token, response):
    github = GithubApi('https://api.github.com', token)
    github._session.request = lambda *args, **kwargs: response
    return github


def test_rate_limit_without_token(capsys):
    github = github_api(None, fake_response(headers=RATE_LIMIT_HEADERS))

    with pytest.raises(SystemExit):
        github.get('/repos/opentofu/opentofu/releases')

    out = capsys.readouterr().out
    assert RELEASES_URL in out
    assert 'Try again when the rate limit resets at' in out
    assert 'GITHUB_DOT_COM_TOKEN' in out


def test_rate_limit_with_token(capsys):
    github = github_api('token', fake_response(headers=RATE_LIMIT_HEADERS))

    with pytest.raises(SystemExit):
        github.get('/repos/opentofu/opentofu/releases')

    out = capsys.readouterr().out
    assert RELEASES_URL in out
    assert 'GITHUB_DOT_COM_TOKEN' not in out


def test_client_error_without_rate_limit_headers(capsys):
    # Not all servers send rate limit headers with client errors
    github = github_api('token', fake_response(status=404, message='Not Found', headers={}))

    response = github.get('/repos/opentofu/opentofu/releases')

    assert response.status_code == 404
    assert 'Not Found' in capsys.readouterr().out


def test_client_error_with_rate_limit_remaining(capsys):
    github = github_api('token', fake_response(status=404, message='Not Found', headers={'X-RateLimit-Remaining': '10', 'X-RateLimit-Limit': '60'}))

    response = github.get('/repos/opentofu/opentofu/releases')

    assert response.status_code == 404
