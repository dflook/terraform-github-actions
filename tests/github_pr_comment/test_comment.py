import random
import string

from github_pr_comment.comment import _format_comment_header, _parse_comment_header, TerraformComment, _to_api_payload, _from_api_payload


def test_comment_header():
    header_args = {
        'workspace_name': 'default',
        'backend_config': 'backend_config1'
    }

    expected_header = '<!-- dflook/terraform-github-actions {"workspace_name":"default","backend_config":"backend_config1"} -->'
    actual_header = _format_comment_header(**header_args)
    assert actual_header == expected_header

    assert _parse_comment_header(expected_header) == header_args

    wonky_header = '<!-- dflook/terraform-github-actions   {   "backend_config"  :"backend_config1" ,  "workspace_name": "default"} -->'
    assert _parse_comment_header(wonky_header) == header_args


def test_no_headers():
    issue_url = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    comment_url = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    status = 'Testing'
    description = 'Hello, this is a description'
    summary = 'Some changes'
    body = '''An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status=status,
        headers={},
        description=description,
        summary=summary,
        body=body
    )

    assert _from_api_payload({
        'body': _to_api_payload(expected),
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_headers():
    issue_url = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    comment_url = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    status = 'Testing'
    description = 'Hello, this is a description'
    summary = 'Some changes'
    body = '''An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
'''
    headers = {
        'hello': 'first_header_value',
        'there': 'second_header_value'
    }

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status=status,
        headers=headers,
        description=description,
        summary=summary,
        body=body
    )

    assert _from_api_payload({
        'body': _to_api_payload(expected),
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_bad_description():
    issue_url = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    comment_url = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    status = 'Testing'
    summary = 'Some changes'
    body = '''blah blah body'''
    description = 'crap -->\nqweqwe</details>something something <details>'

    headers = {
        'hello': 'first_header_value',
        'there': 'second_header_value'
    }

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status=status,
        headers=headers,
        description=description,
        summary=summary,
        body=body
    )

    assert _from_api_payload({
        'body': _to_api_payload(expected),
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_bad_body():
    issue_url = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    comment_url = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    status = 'Testing'
    summary = 'Some changes'
    description = '''blah blah description'''
    body = 'qweqwe</details>something something ```</details>'

    headers = {
        'hello': 'first_header_value',
        'there': 'second_header_value'
    }

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status=status,
        headers=headers,
        description=description,
        summary=summary,
        body=body
    )

    assert _from_api_payload({
        'body': _to_api_payload(expected),
        'url': comment_url,
        'issue_url': issue_url
    }) == expected
