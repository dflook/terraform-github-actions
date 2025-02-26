from action import Input

auto_approve = Input(
    name='auto_approve',
    type='bool',
    description='''
When set to `true`, plans are always applied.

The default is `false`, which requires plans to have been added to a pull request comment.
''',
    required=False,
    default='false'
)
