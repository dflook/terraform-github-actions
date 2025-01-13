import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from environment_variables.TERRAFORM_HTTP_CREDENTIALS import TERRAFORM_HTTP_CREDENTIALS
from environment_variables.TERRAFORM_PRE_RUN import TERRAFORM_PRE_RUN
from environment_variables.TERRAFORM_SSH_KEY import TERRAFORM_SSH_KEY
from inputs.path import path
from inputs.test_directory import test_directory
from inputs.test_filter import test_filter
from inputs.var_file import var_file
from inputs.variables import variables
from outputs.failure_reason import failure_reason

test = Action(
    'test',
    '''
    Execute automated tests on a $ProductName module using the built-in `$ToolName test` command.
    If the tests fail, the job will stop with a failure status.
    ''',
    meta_description='Execute automated tests for a $ProductName module',
    inputs=[
        dataclasses.replace(path, description='The path to the $ProductName module under test'),
        test_directory,
        test_filter,
        dataclasses.replace(variables, description='''
            Variables to set for the tests. This should be valid $ProductName syntax - like a [variable definition file]($VariableDefinitionUrl).
            Variables set here override any given in `var_file`s.
        '''),
        var_file
    ],
    outputs=[
        dataclasses.replace(failure_reason, description='''
          When the job outcome is `failure`, this output may be set. The value may be one of:
        
          - `no-tests` - No tests were found to run.
          - `tests-failed` - One or more tests failed.
        
          If the job fails for any other reason this will not be set.
          This can be used with the Actions expression syntax to conditionally run steps.
        ''')
    ],
    environment_variables=[
        GITHUB_DOT_COM_TOKEN,
        TERRAFORM_CLOUD_TOKENS,
        TERRAFORM_SSH_KEY,
        TERRAFORM_HTTP_CREDENTIALS,
        TERRAFORM_PRE_RUN
    ],
    extra='''
## Example usage

```yaml
name: "Run Tests"

on: [push]

jobs:
  test:
    name: Unlock
    runs-on: ubuntu-latest
    steps:
      - name: Checkout current branch
        uses: actions/checkout@v4

      - name: $ProductName Tests
        uses: dflook/$ToolName-test@v1
        with:
          path: modules/vpc
```
'''
)