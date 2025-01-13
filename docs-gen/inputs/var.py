from action import Input

var = Input(
    name='var',
    type='string',
    description='''
Comma separated list of $ProductName vars to set.
This is deprecated due to the following limitations:
- Only primitive types can be set with `var` - number, bool and string.
- String values may not contain a comma.
- Values set with `var` will be overridden by values contained in `var_file`s
- Does not work with the `remote` backend
You can change from `var` to `variables` by putting each variable on a separate line and ensuring each string value is quoted.
''',
    example='''
```yaml
with:
  var: instance_type=m5.xlarge,nat_type=instance
```
Becomes:
```yaml
with:
  variables: |
    instance_type="m5.xlarge"
    nat_type="instance"
```
''',
    required=False,
    deprecation_message='Use the variables input instead.',
    #default='',
    show_in_docs=False
)
