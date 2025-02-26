from action import Input

add_github_comment = Input(
    name='add_github_comment',
    type='string',
    description='''
Controls whether a comment is added to the PR with the generated plan.

The default is `true`, which adds a comment to the PR with the results of the plan.
Set to `changes-only` to add a comment only when the plan indicates there are changes to apply.
Set to `always-new` to always create a new comment for each plan, instead of updating the previous comment.
Set to `false` to disable the comment - the plan will still appear in the workflow log.
''',
    required=False,
    default='true'
)
