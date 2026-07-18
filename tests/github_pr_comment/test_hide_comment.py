from unittest.mock import MagicMock

from github_pr_comment.comment import hide_comment, TerraformComment


def test_hide_comment_uses_graphql_variables(monkeypatch):
    monkeypatch.setenv('GITHUB_API_URL', 'https://api.github.com')

    mock_github = MagicMock()

    comment = TerraformComment(
        issue_url='https://api.github.com/repos/test/test/issues/1',
        comment_url='https://api.github.com/repos/test/test/issues/comments/123',
        node_id='MDEyOk_test_node_id',
        headers={},
        description='test',
        summary='test',
        body='test',
        status='test'
    )

    hide_comment(mock_github, comment, 'OUTDATED')

    mock_github.graphql.assert_called_once_with(json={
            'query': 'mutation($input: MinimizeCommentInput!) { minimizeComment(input: $input) { clientMutationId } }',
            'variables': {
                'input': {
                    'subjectId': 'MDEyOk_test_node_id',
                    'classifier': 'OUTDATED'
                }
            }
        }
    )


def test_hide_comment_skips_when_no_node_id(monkeypatch):
    monkeypatch.setenv('GITHUB_API_URL', 'https://api.github.com')

    mock_github = MagicMock()

    comment = TerraformComment(
        issue_url='https://api.github.com/repos/test/test/issues/1',
        comment_url='https://api.github.com/repos/test/test/issues/comments/123',
        node_id=None,
        headers={},
        description='test',
        summary='test',
        body='test',
        status='test'
    )

    hide_comment(mock_github, comment, 'OUTDATED')

    mock_github.graphql.assert_not_called()
