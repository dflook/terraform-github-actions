from github_pr_comment.__main__ import get_backend_fingerprints
from github_pr_comment.backend_config import complete_config, legacy_complete_config, legacy_partial_config, COMPLETE_FINGERPRINT_SINCE_VERSION, FIXED_FINGERPRINT_SINCE_VERSION
from github_pr_comment.backend_fingerprint import fingerprint
from github_pr_comment.comment import find_comment, matching_headers, BackupHeaders, TerraformComment, _to_api_payload, _format_comment_header, _parse_comment_header
from github_pr_comment.hash import comment_hash
from terraform.hcl import loads

ISSUE_URL = 'https://api.github.com/repos/dflook/test/issues/1'
PR_URL = 'https://api.github.com/repos/dflook/test/pulls/1'
COMMENT_URL = 'https://api.github.com/repos/dflook/test/issues/comments/2'

COMPLETE_VERSION = COMPLETE_FINGERPRINT_SINCE_VERSION
FIXED_VERSION = FIXED_FINGERPRINT_SINCE_VERSION


class StubGithub:
    def __init__(self, comments):
        self._comments = comments

    def paged_get(self, url, **kwargs):
        yield from self._comments


def comment_payload(comment):
    return {
        'body': _to_api_payload(comment),
        'issue_url': comment.issue_url,
        'url': comment.comment_url,
        'node_id': comment.node_id,
        'user': {'login': 'test-user'}
    }


def get_fingerprints(monkeypatch, tmp_path, backend_config_file=''):
    monkeypatch.setenv('TF_DATA_DIR', str(tmp_path))

    module = loads('''
terraform {
  backend pg {}
}
    ''')

    inputs = {
        'INPUT_BACKEND_CONFIG_FILE': backend_config_file,
        'INPUT_BACKEND_CONFIG': 'conn_str=postgres://host/db?sslmode=disable'
    }

    fingerprints = {}
    for name, config in [
        ('complete', complete_config),
        ('legacy_complete', legacy_complete_config),
        ('legacy_partial', legacy_partial_config),
    ]:
        backend_type, backend_config = config(inputs, module)
        fingerprints[name] = fingerprint(backend_type, backend_config, {})

    return fingerprints


def make_comment(backend_hash, version=None):
    headers = {'workspace': 'default', 'backend': backend_hash, 'plan_hash': 'p1'}
    if version is not None:
        headers['version'] = version

    return TerraformComment(
        issue_url=ISSUE_URL,
        comment_url=COMMENT_URL,
        node_id='node',
        headers=headers,
        description='Terraform plan in __.__',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body='+ resource "random_string" "s"',
        status=':memo: Plan generated',
    )


def search_headers(fingerprints):
    """The primary and backup headers, as constructed by github_pr_comment.__main__"""

    def backup(name, min_version, max_version):
        return BackupHeaders({'workspace': 'default', 'closed': None, 'label': None, 'backend': comment_hash(fingerprints[name], PR_URL)}, min_version, max_version)

    headers = {'workspace': 'default', 'closed': None, 'label': None, 'backend': comment_hash(fingerprints['complete'], PR_URL)}
    backup_headers = [
        backup('legacy_complete', COMPLETE_VERSION, FIXED_VERSION),
        backup('legacy_partial', None, COMPLETE_VERSION),
    ]
    return headers, backup_headers


def test_find_comment_created_before_backend_config_parse_fix(monkeypatch, tmp_path):
    """A comment created with the old backend_config parsing must still be found, e.g. by an apply after merge."""

    fingerprints = get_fingerprints(monkeypatch, tmp_path)

    # The premise: the fixed parse produces a different fingerprint for this input
    assert fingerprints['complete'] != fingerprints['legacy_complete']

    old_comment = make_comment(comment_hash(fingerprints['legacy_complete'], PR_URL), version='2.2.3')
    headers, backup_headers = search_headers(fingerprints)

    github = StubGithub([comment_payload(old_comment)])
    found = find_comment(github, ISSUE_URL, 'test-user', headers, backup_headers, 'legacy description')

    # The old comment is found, and its headers are updated with the current fingerprint
    assert found.comment_url == COMMENT_URL
    assert found.headers['backend'] == comment_hash(fingerprints['complete'], PR_URL)

    # The approval headers survive the merge
    assert found.headers['plan_hash'] == 'p1'

    # None valued search headers must not leak into the comment headers, or the comment
    # becomes unmatchable once they are written back
    assert 'closed' not in found.headers
    assert 'label' not in found.headers

    # After the headers are written back to the comment, the next run must still match it
    rewritten = _parse_comment_header(_format_comment_header(**found.headers))
    rewritten_comment = TerraformComment(
        issue_url=ISSUE_URL, comment_url=COMMENT_URL, node_id='node', headers=rewritten,
        description='d', summary='s', body='b', status='')
    assert matching_headers(rewritten_comment, headers)


def test_find_comment_unversioned_comment_matches_backup(monkeypatch, tmp_path):
    """A comment without a version header predates version stamping and may match any unbounded backup set."""

    fingerprints = get_fingerprints(monkeypatch, tmp_path)

    old_comment = make_comment(comment_hash(fingerprints['legacy_partial'], PR_URL))
    headers, backup_headers = search_headers(fingerprints)

    github = StubGithub([comment_payload(old_comment)])
    found = find_comment(github, ISSUE_URL, 'test-user', headers, backup_headers, 'legacy description')

    assert found.comment_url == COMMENT_URL
    assert found.headers['backend'] == comment_hash(fingerprints['complete'], PR_URL)


def test_find_comment_with_current_fingerprint(monkeypatch, tmp_path):
    fingerprints = get_fingerprints(monkeypatch, tmp_path)

    current_comment = make_comment(comment_hash(fingerprints['complete'], PR_URL), version=FIXED_VERSION)
    headers, backup_headers = search_headers(fingerprints)

    github = StubGithub([comment_payload(current_comment)])
    found = find_comment(github, ISSUE_URL, 'test-user', headers, backup_headers, 'legacy description')

    assert found.comment_url == COMMENT_URL
    assert found.headers['backend'] == comment_hash(fingerprints['complete'], PR_URL)


def test_find_comment_newer_comments_not_matched_by_backup_headers(monkeypatch, tmp_path):
    """A comment created by a version outside a backup set's range must not match it.

    This prevents a comment whose genuine fingerprint collides with a legacy fingerprint
    (e.g. pg with conn_str set by environment variable) being claimed by another module's plan.
    """

    fingerprints = get_fingerprints(monkeypatch, tmp_path)
    headers, backup_headers = search_headers(fingerprints)

    # This comment's backend hash equals the legacy backup hash, but it was created by a fixed version
    collision_comment = make_comment(comment_hash(fingerprints['legacy_complete'], PR_URL), version=FIXED_VERSION)

    github = StubGithub([comment_payload(collision_comment)])
    found = find_comment(github, ISSUE_URL, 'test-user', headers, backup_headers, 'legacy description')

    assert found.comment_url is None


def test_find_comment_unversioned_comment_not_matched_by_min_bounded_backup(monkeypatch, tmp_path):
    """A comment without a version header must not match a backup set with a minimum version.

    Complete fingerprints were only ever written by versions that also stamp a version header,
    so an unversioned comment can't carry one.

    A backend config file is used so the partial and complete fingerprints differ.
    """

    fingerprints = get_fingerprints(monkeypatch, tmp_path, backend_config_file='tests/github_pr_comment/test_backend_file.tfvars')
    headers, backup_headers = search_headers(fingerprints)

    unversioned_comment = make_comment(comment_hash(fingerprints['legacy_complete'], PR_URL))

    github = StubGithub([comment_payload(unversioned_comment)])
    found = find_comment(github, ISSUE_URL, 'test-user', headers, backup_headers, 'legacy description')

    assert found.comment_url is None


def test_find_comment_stale_stamp_era(monkeypatch, tmp_path):
    """Versions 1.32.0-1.32.1 stamped comments with '1.31.1' - they must match the legacy complete fingerprint."""

    fingerprints = get_fingerprints(monkeypatch, tmp_path)
    headers, backup_headers = search_headers(fingerprints)

    stale_stamp_comment = make_comment(comment_hash(fingerprints['legacy_complete'], PR_URL), version='1.31.1')

    github = StubGithub([comment_payload(stale_stamp_comment)])
    found = find_comment(github, ISSUE_URL, 'test-user', headers, backup_headers, 'legacy description')

    assert found.comment_url == COMMENT_URL
    assert found.headers['backend'] == comment_hash(fingerprints['complete'], PR_URL)


def test_backup_fingerprint_windows_merge_on_collision(monkeypatch, tmp_path):
    """With no backend config files, the legacy complete and partial fingerprints are identical.

    The merged entry must keep min_version=None, so unversioned comments from before
    version stamping are still matched.
    """

    monkeypatch.setenv('TF_DATA_DIR', str(tmp_path))

    module = loads('''
terraform {
  backend pg {}
}
    ''')

    inputs = {
        'INPUT_BACKEND_CONFIG_FILE': '',
        'INPUT_BACKEND_CONFIG': 'conn_str=postgres://host/db?sslmode=disable'
    }

    primary, backups = get_backend_fingerprints(inputs, module)

    assert len(backups) == 1
    backup_fingerprint, min_version, max_version = backups[0]
    assert min_version is None
    assert max_version == FIXED_VERSION

    headers = {'workspace': 'default', 'closed': None, 'label': None, 'backend': comment_hash(primary, PR_URL)}
    backup_headers = [
        BackupHeaders({'workspace': 'default', 'closed': None, 'label': None, 'backend': comment_hash(backup_fingerprint, PR_URL)}, min_version, max_version)
    ]

    unversioned_comment = make_comment(comment_hash(backup_fingerprint, PR_URL))

    github = StubGithub([comment_payload(unversioned_comment)])
    found = find_comment(github, ISSUE_URL, 'test-user', headers, backup_headers, 'legacy description')

    assert found.comment_url == COMMENT_URL


def test_find_comment_dev_stamped_comment(monkeypatch, tmp_path):
    """Comments stamped with a placeholder version (images built without a release version) may be from any era."""

    fingerprints = get_fingerprints(monkeypatch, tmp_path)
    headers, backup_headers = search_headers(fingerprints)

    dev_comment = make_comment(comment_hash(fingerprints['legacy_complete'], PR_URL), version='99.0.0')

    github = StubGithub([comment_payload(dev_comment)])
    found = find_comment(github, ISSUE_URL, 'test-user', headers, backup_headers, 'legacy description')

    assert found.comment_url == COMMENT_URL


def test_find_comment_null_header_values_are_scrubbed(monkeypatch, tmp_path):
    """Old versions could write literal null header values, which made comments unmatchable."""

    fingerprints = get_fingerprints(monkeypatch, tmp_path)
    headers, backup_headers = search_headers(fingerprints)

    poisoned_comment = TerraformComment(
        issue_url=ISSUE_URL,
        comment_url=COMMENT_URL,
        node_id='node',
        headers={'workspace': 'default', 'backend': comment_hash(fingerprints['complete'], PR_URL), 'plan_hash': 'p1', 'version': '2.2.3', 'closed': None, 'label': None},
        description='d', summary='s', body='b', status='')

    github = StubGithub([comment_payload(poisoned_comment)])
    found = find_comment(github, ISSUE_URL, 'test-user', headers, backup_headers, 'legacy description')

    assert found.comment_url == COMMENT_URL
    assert 'closed' not in found.headers
    assert 'label' not in found.headers


def test_find_comment_ignores_other_backends(monkeypatch, tmp_path):
    fingerprints = get_fingerprints(monkeypatch, tmp_path)

    other_comment = make_comment(comment_hash(b'a completely different backend', PR_URL))
    headers, backup_headers = search_headers(fingerprints)

    github = StubGithub([comment_payload(other_comment)])
    found = find_comment(github, ISSUE_URL, 'test-user', headers, backup_headers, 'legacy description')

    # No match - a new comment would be created
    assert found.comment_url is None
