from action import Input

workspace = Input(
    name='workspace',
    type='string',
    description='The $ProductName workspace to use.',
    default='default',
    required=False
)
