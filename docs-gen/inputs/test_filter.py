from action import Input

test_filter = Input(
    name='test_filter',
    type='string',
    description='''
      The test files to run, one per line.
      
      If not specified, all test files in the `test_directory` will be run.
      The are paths relative to the module path.
    ''',
    example='''
      ```yaml
      with:
        test_filter: |
          tests/main.tftest.hcl
          tests/other.tftest.hcl
      ```
    ''',
    required=False,
    default='',
    default_description='All test files in the `test_directory`.'
)
