from action import Input

backend_config = Input(
    name='backend_config',
    type='string',
    description='''
List of $ProductName backend config values, one per line.
''',
    example='''
```yaml
with:
  backend_config: token=${{ secrets.BACKEND_TOKEN }}
```
''',
    required=False,
    default=''
)
