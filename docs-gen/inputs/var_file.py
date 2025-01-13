from action import Input

var_file = Input(
    name='var_file',
    type='string',
    description='''
List of tfvars files to use, one per line.
Paths should be relative to the GitHub Actions workspace
''',
    example='''
```yaml
with:
  var_file: |
    common.tfvars
    prod.tfvars
```
''',
    required=False,
)
