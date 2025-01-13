from action import Input

backend_config_arguments = Input(
    name='backend_config_arguments',
    type='string',
    description='''
Backend configuration arguments for completing a partial backend configuration. This should be valid $ProductName syntax - like a [backend configuration file](https://developer.hashicorp.com/terraform/language/backend#file).
''',
    example='''
```yaml
with:
  backend_config_arguments: |
    address = "demo.consul.io"
    path    = "example_app/$ToolName_state"
    scheme  = "https"
```
''',
    required=False,
    default=''
)
