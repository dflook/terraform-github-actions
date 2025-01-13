from action import Input

variables = Input(
    name='variables',
    type='string',
    description='''
Variables to set for the $ToolName plan. This should be valid $ProductName syntax - like a [variable definition file]($VariableDefinitionUrl).

Variables set here override any given in `var_file`s.
''',
    example='''
```yaml
with:
  variables: |
    image_id = "${{ secrets.AMI_ID }}"
    availability_zone_names = [
      "us-east-1a",
      "us-west-1c",
    ]
```
''',
    required=False
)
