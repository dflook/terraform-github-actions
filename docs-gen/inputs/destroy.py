from action import Input

destroy = Input(
    name='destroy',
    type='boolean',
    description='''
Set to `true` to generate a plan to destroy all resources.

This generates a plan in [destroy mode]($DestroyModeUrl).
''',
    required=False,
    default='false'
)
