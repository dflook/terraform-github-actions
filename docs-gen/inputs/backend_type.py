from action import Input

backend_type = Input(
    name='backend_type',
    type='string',
    description='''
The name of the $ProductName plugin used for backend state
''',
    required=True,
)
