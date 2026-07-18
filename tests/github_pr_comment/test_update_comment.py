from github_pr_comment.comment import update_comment, TerraformComment

ISSUE_URL = 'https://api.github.com/repos/dflook/test/issues/1'
COMMENT_URL = 'https://api.github.com/repos/dflook/test/issues/comments/2'


class StubResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class StubGithub:
    def __init__(self, payload):
        self._payload = payload

    def patch(self, url, json):
        return StubResponse(self._payload)

    def post(self, url, json):
        return StubResponse(self._payload)


def test_update_learns_node_id():
    comment = TerraformComment(
        issue_url=ISSUE_URL,
        comment_url=COMMENT_URL,
        node_id=None,
        headers={'workspace': 'default'},
        description='d', summary='s', body='b', status='st')

    github = StubGithub({'url': COMMENT_URL, 'node_id': 'N1'})
    updated = update_comment(github, comment, status='new status')

    # The learned node_id must be on the returned comment, which is serialized to the step cache
    assert updated.node_id == 'N1'
    assert updated.status == 'new status'
    assert updated.body == 'b'

    # It is also set on the passed comment, which the always-new flow keeps using
    assert comment.node_id == 'N1'


def test_update_keeps_known_node_id():
    comment = TerraformComment(
        issue_url=ISSUE_URL,
        comment_url=COMMENT_URL,
        node_id='N0',
        headers={'workspace': 'default'},
        description='d', summary='s', body='b', status='st')

    github = StubGithub({'url': COMMENT_URL, 'node_id': 'N1'})
    updated = update_comment(github, comment, status='new status')

    assert updated.node_id == 'N0'
    assert comment.node_id == 'N0'


def test_create_sets_node_id():
    comment = TerraformComment(
        issue_url=ISSUE_URL,
        comment_url=None,
        node_id=None,
        headers={'workspace': 'default'},
        description='d', summary='s', body='b', status='st')

    github = StubGithub({'url': COMMENT_URL, 'node_id': 'N1'})
    created = update_comment(github, comment, status='st')

    assert created.comment_url == COMMENT_URL
    assert created.node_id == 'N1'
