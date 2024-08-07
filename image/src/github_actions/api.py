import datetime
import re
import sys
from typing import NewType, Iterable, Any, Optional

import requests
from requests import Response
from requests_cache import CachedSession, EXPIRE_IMMEDIATELY
from github_actions.debug import debug

GitHubUrl = NewType('GitHubUrl', str)
PrUrl = NewType('PrUrl', GitHubUrl)
IssueUrl = NewType('IssueUrl', GitHubUrl)
CommentUrl = NewType('CommentUrl', GitHubUrl)
CommentReactionUrl = NewType('CommentReactionUrl', GitHubUrl)
NodeId = NewType('NodeId', str)


class GithubApi:
    def __init__(self, host: str, token: Optional[str], cache_path: Optional[str] = None):
        self._host = host
        self._token = token

        if cache_path is not None:
            urls_expire_after = {
                re.compile(r'/repos/.*/.*/issues/\d+/comments'): 60 * 60 * 24 * 3,
                re.compile(r'/repositories/.*/issues/.*/comments'): 60 * 60 * 24 * 3,
                '*': EXPIRE_IMMEDIATELY
            }

            self._session = CachedSession(backend='sqlite', cache_name=f'{cache_path}/github_api_cache', urls_expire_after=urls_expire_after, always_revalidate=True)
            self._session.cache.delete(expired=True)
        else:
            self._session = requests.Session()

        if token is not None:
            self._session.headers['authorization'] = f'token {token}'

        self._session.headers['user-agent'] = 'terraform-github-actions'
        self._session.headers['accept'] = 'application/vnd.github.v3+json'

    def api_request(self, method: str, *args, **kwargs) -> requests.Response:
        response = self._session.request(method, *args, **kwargs)
        debug(f'{response.request.method} {response.request.url} -> {response.status_code}')

        if 400 <= response.status_code < 500:
            try:
                message = response.json()['message']

                if response.headers['X-RateLimit-Remaining'] == '0' and response.headers['X-RateLimit-Limit'] != '0':
                    limit_reset = datetime.datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))
                    sys.stdout.write(message)
                    sys.stdout.write(f' Try again when the rate limit resets at {limit_reset} UTC.\n')
                    sys.exit(1)

                if message not in ['Resource not accessible by integration', 'Personal access tokens with fine grained access do not support the GraphQL API']:
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

            if hasattr(response, 'from_cache'):
                debug(f'Cache hit: {response.from_cache}')

            yield from response.json()

            if 'next' in response.links:
                if 'params' in kwargs:
                    # Relevant params are already in the link URL
                    del kwargs['params']
                url = response.links['next']['url']
            else:
                return
