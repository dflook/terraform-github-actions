from action import Input

replace = Input(
    name='replace',
    type='string',
    description='''
List of resources to replace, one per line.
''',
    example='''
```yaml
with:
  replace: |
    random_password.database
```
  ''',
    default='',
    required=False
)
