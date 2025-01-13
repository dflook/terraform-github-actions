from action import Input

backend_config_file = Input(
    name='backend_config_file',
    type='string',
    description='''
List of $ProductName backend config files to use, one per line.
Paths should be relative to the GitHub Actions workspace
''',
    example='''
```yaml
with:
  backend_config_file: prod.backend.tfvars
```
''',
    required=False,
    default=''
)
