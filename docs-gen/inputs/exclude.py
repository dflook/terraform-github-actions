from action import Input, OpenTofu

exclude = Input(
    name='exclude',
    type='string',
    description='''
List of resources to exclude from operations, one per line.
The plan will include all resources except the specified ones and their dependencies.

Requires OpenTofu 1.9+.
''',
    example='''
```yaml
with:
  exclude: |
    local_file.sensitive_config
    aws_instance.temp_resource
```
''',
    default='',
    required=False,
    available_in=[OpenTofu]
)