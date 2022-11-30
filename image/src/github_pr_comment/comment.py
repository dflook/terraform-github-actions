import json
import os
import re
from json import JSONDecodeError
from typing import Optional, Any

from github_actions.api import IssueUrl, GithubApi, CommentUrl
from github_actions.debug import debug

try:
    collapse_threshold = int(os.environ['TF_PLAN_COLLAPSE_LENGTH'])
except (ValueError, KeyError):
    collapse_threshold = 10

from pkg_resources import get_distribution, DistributionNotFound

try:
    version = get_distribution('terraform-github-actions').version
except DistributionNotFound:
    version = '0.0.0'

class TerraformComment:
    """
    Represents a Terraform PR comment

    The comment must have been successfully created for an object of this type to have been created.

    A Terraform PR comment has a number of elements that are formatted such that they can later be parsed back into
    an equivalent TerraformComment object.

    header_fields = [
        'workspace',      # The terraform workspace
        'backend',        # A fingerprint of the backend config
        'label',          # The label input
        'backend_type',   # The backend type name
        'plan_modifier',  # Hash of plan modifiers (target/replace options)
        'plan_job_ref',   # A text reference to the actions job that generated the plan
        'plan_hash',      # A deterministic hash of the plan (without warnings or unchanged attributes, eventually with unmasked variables)
        'variables_hash', # A hash of input variables and values
        'truncated'       # If the plan text has been truncated (should not be used to approve plans, and will not show a complete diff)
    ]

    """

    def __init__(self, *, issue_url: IssueUrl, comment_url: Optional[CommentUrl], headers: dict[str, str], description: str, summary: str, body: str, status: str):
        self._issue_url = issue_url
        self._comment_url = comment_url
        self._headers = headers
        self._description = description.strip()
        self._summary = summary.strip()
        self._body = body.strip()
        self._status = status.strip()

    def __eq__(self, other):
        if not isinstance(other, TerraformComment):
            return NotImplemented

        return (
            self._issue_url == other._issue_url and
            self._comment_url == other._comment_url and
            self._headers == other._headers and
            self._description == other._description and
            self._summary == other._summary and
            self._body == other._body and
            self._status == other._status
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f'TerraformComment(issue_url={self._issue_url!r}, comment_url={self._comment_url!r}, headers={self._headers!r}, description={self._description!r}, summary={self._summary!r}, body={self._body!r}, status={self._status!r})'

    @property
    def comment_url(self) -> Optional[CommentUrl]:
        return self._comment_url

    @comment_url.setter
    def comment_url(self, comment_url: CommentUrl) -> None:
        if self._comment_url is not None:
            raise Exception('Can only set url for comments that don\'t exist yet')
        self._comment_url = comment_url

    @property
    def issue_url(self) -> IssueUrl:
        return self._issue_url

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @property
    def description(self) -> str:
        return self._description

    @property
    def summary(self) -> str:
        return self._summary

    @property
    def body(self) -> str:
        return self._body

    @property
    def status(self) -> str:
        return self._status

def serialize(comment: TerraformComment) -> str:
    return json.dumps({
        'issue_url': comment.issue_url,
        'comment_url': comment.comment_url,
        'headers': comment.headers,
        'description': comment.description,
        'summary': comment.summary,
        'body': comment.body,
        'status': comment.status
    })

def deserialize(s) -> TerraformComment:
    j = json.loads(s)

    return TerraformComment(
        issue_url=j['issue_url'],
        comment_url=j['comment_url'],
        headers=j['headers'],
        description=j['description'],
        summary=j['summary'],
        body=j['body'],
        status=j['status']
    )

def _format_comment_header(**kwargs) -> str:
    return f'<!-- dflook/terraform-github-actions {json.dumps(kwargs, separators=(",",":"))} -->'

def _parse_comment_header(comment_header: Optional[str]) -> dict[str, str]:
    if comment_header is None:
        return {}

    if header := re.match(r'^<!--\sdflook/terraform-github-actions\s(?P<args>.*)\s-->', comment_header):
        try:
            return json.loads(header['args'])
        except JSONDecodeError:
            return {}

    return {}


def _from_api_payload(comment: dict[str, Any]) -> Optional[TerraformComment]:
    match = re.match(r'''
            (?P<headers><!--.*?-->\n)?
            (?P<description>.*)
            <details(?:\sopen)?>\s*
            (?:<summary>(?P<summary>.*?)</summary>\s*)?
            ```(?:hcl)?
            (?P<body>.*)
            ```\s*
            </details>
            (?P<status>.*)
        ''',
        comment['body'],
        re.VERBOSE | re.DOTALL
    )

    if not match:
        return None

    return TerraformComment(
        issue_url=comment['issue_url'],
        comment_url=comment['url'],
        headers=_parse_comment_header(match.group('headers')),
        description=match.group('description').strip(),
        summary=match.group('summary').strip(),
        body=match.group('body').strip(),
        status=match.group('status').strip()
    )


def _to_api_payload(comment: TerraformComment) -> str:
    details_open = False
    hcl_highlighting = False

    if comment.body.startswith('Error'):
        details_open = True
    elif 'Plan:' in comment.body:
        hcl_highlighting = True
        num_lines = len(comment.body.splitlines())
        if num_lines < collapse_threshold:
            details_open = True

    if comment.summary is None:
        details_open = True

    header = _format_comment_header(**comment.headers)

    body = f'''{header}
{comment.description}
<details{' open' if details_open else ''}>
{f'<summary>{comment.summary}</summary>' if comment.summary is not None else ''}

```{'hcl' if hcl_highlighting else ''}
{comment.body}
```
</details>
'''

    if comment.status:
        body += '\n' + comment.status

    return body

def matching_headers(comment: TerraformComment, headers: dict[str, str]) -> bool:
    """
    Does a comment have all the specified headers

    Additional headers may be present in the comment, they are ignored if not specified in the headers argument.
    If a header should NOT be present in the comment, specify a header with a value of None
    """

    for header, value in headers.items():
        if value is None and header in comment.headers:
            return False

        if value is not None and comment.headers.get(header) != value:
            return False

    return True

def find_comment(github: GithubApi, issue_url: IssueUrl, username: str, headers: dict[str, str], backup_headers: dict[str, str], legacy_description: str) -> TerraformComment:
    """
    Find a github comment that matches the given headers

    If no comment is found with the specified headers, tries to find a comment that matches the specified description instead.
    This is in case the comment was made with an earlier version, where comments were matched by description only.

    If not existing comment is found a new TerraformComment object is returned which represents a PR comment yet to be created.

    :param github: The github api object to make requests with
    :param issue_url: The issue to find the comment in
    :param username: The user who made the comment
    :param headers: The headers that must be present on the comment
    :param legacy_description: The description that must be present on the comment, if not headers are found.
    """

    debug(f"Searching for comment with {headers=}")
    debug(f"Or backup headers {backup_headers=}")

    backup_comment = None
    legacy_comment = None

    for comment_payload in github.paged_get(issue_url + '/comments'):
        if comment_payload['user']['login'] != username:
            continue

        if comment := _from_api_payload(comment_payload):

            if comment.headers:
                # Match by headers only

                if matching_headers(comment, headers):
                    debug(f'Found comment that matches headers {comment.headers=} ')
                    return comment

                if matching_headers(comment, backup_headers):
                    debug(f'Found comment that matches backup headers {comment.headers=} ')
                    backup_comment = comment
                else:
                    debug(f"Didn't match comment with {comment.headers=}")

            else:
                # Match by description only

                if comment.description == legacy_description and legacy_comment is None:
                    debug(f'Found comment that matches legacy description {comment.description=}')
                    legacy_comment = comment
                else:
                    debug(f"Didn't match comment with {comment.description=}")

    if backup_comment is not None:
        debug('Using comment matching backup headers')

        # Use the backup comment but update the headers
        return TerraformComment(
            issue_url=backup_comment.issue_url,
            comment_url=backup_comment.comment_url,
            headers=backup_comment.headers | headers,
            description=backup_comment.description,
            summary=backup_comment.summary,
            body=backup_comment.body,
            status=backup_comment.status
        )

    if legacy_comment is not None:
        debug('Using comment matching legacy description')

        # Insert known headers into legacy comment
        return TerraformComment(
            issue_url=legacy_comment.issue_url,
            comment_url=legacy_comment.comment_url,
            headers={k: v for k, v in headers.items() if v is not None},
            description=legacy_comment.description,
            summary=legacy_comment.summary,
            body=legacy_comment.body,
            status=legacy_comment.status
        )

    debug('No existing comment exists')
    return TerraformComment(
        issue_url=issue_url,
        comment_url=None,
        headers={k: v for k, v in headers.items() if v is not None},
        description='',
        summary='',
        body='',
        status=''
    )


def update_comment(
    github: GithubApi,
    comment: TerraformComment,
    *,
    headers: dict[str, str] = None,
    description: str = None,
    summary: str = None,
    body: str = None,
    status: str = None
) -> TerraformComment:

    new_headers = headers if headers is not None else comment.headers
    new_headers['version'] = version

    new_comment = TerraformComment(
        issue_url=comment.issue_url,
        comment_url=comment.comment_url,
        headers=new_headers,
        description=description if description is not None else comment.description,
        summary=summary if summary is not None else comment.summary,
        body=body if body is not None else comment.body,
        status=status if status is not None else comment.status
    )

    if comment.comment_url is not None:
        response = github.patch(comment.comment_url, json={'body': _to_api_payload(new_comment)})
        response.raise_for_status()
    else:
        response = github.post(comment.issue_url + '/comments', json={'body': _to_api_payload(new_comment)})
        response.raise_for_status()
        new_comment.comment_url = response.json()['url']

    return new_comment
