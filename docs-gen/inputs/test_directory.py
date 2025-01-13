from action import Input

test_directory = Input(
    name='test_directory',
    type='string',
    description='''
The directory within the module path that contains the test files.
''',
    example='''
```yaml
with:
  test_directory: tf_tests
```
''',
    required=False,
    default='',
    default_description='`tests`'
)
