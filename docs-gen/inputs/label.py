from action import Input

label = Input(
    name='label',
    type='string',
    description='''
A friendly name for the environment the $ProductName configuration is for.
This will be used in the PR comment for easy identification.
    ''',
    required=False,
    default=""
)
