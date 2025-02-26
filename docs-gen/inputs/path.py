from action import Input

path = Input(
    name='path',
    type='string',
    description='The path to the $ProductName root module directory.',
    default='.',
    default_description='The action workspace',
    required=False
)
