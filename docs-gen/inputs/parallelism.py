from action import Input

parallelism = Input(
    name='parallelism',
    type='number',
    description='''
Limit the number of concurrent operations
''',
    required=False,
    default='0',
    default_description='The $ProductName default (10).'
)
