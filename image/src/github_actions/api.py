import datetime
import sys
from typing import NewType, Iterable, Any

import requests
from requests import Response

from github_actions.debug import debug

GitHubUrl = NewType('GitHubUrl', str)
PrUrl = NewType('PrUrl', GitHubUrl)
IssueUrl = NewType('IssueUrl', GitHubUrl)
CommentUrl = NewType('CommentUrl', GitHubUrl)


class GithubApi:
    def __init__(self, host: str, token: str):
        self._host = host
        self._token = token

        self._session = requests.Session()
        self._session.headers['authorization'] = f'token {token}'
        self._session.headers['user-agent'] = 'terraform-github-actions'
        self._session.headers['accept'] = 'application/vnd.github.v3+json'

    def api_request(self, method: str, *args, **kwargs) -> requests.Response:
        response = self._session.request(method, *args, **kwargs)

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

    def get(self, path: str, **kwargs: Any) -> Response:
        return self.api_request('GET', path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Response:
        return self.api_request('POST', path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Response:
        return self.api_request('PATCH', path, **kwargs)

    def paged_get(self, url: GitHubUrl, *args, **kwargs) -> Iterable[dict[str, Any]]:
        while True:
            response = self.api_request('GET', url, *args, **kwargs)
            response.raise_for_status()

            yield from response.json()

            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                return
