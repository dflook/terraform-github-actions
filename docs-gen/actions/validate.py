import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from environment_variables.TERRAFORM_HTTP_CREDENTIALS import TERRAFORM_HTTP_CREDENTIALS
from environment_variables.TERRAFORM_PRE_RUN import TERRAFORM_PRE_RUN
from environment_variables.TERRAFORM_SSH_KEY import TERRAFORM_SSH_KEY
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.path import path
from inputs.workspace import workspace
from outputs.failure_reason import failure_reason

backend_reason = '''
This is used for discovering the $ProductName version to use, if not otherwise specified. 
See [dflook/$ToolName-version](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-version#$ToolName-version-action) for details.
'''.strip()

validate = Action(
    'validate',
    '''
    This action uses the `$ToolName validate` command to check that a $ProductName configuration is valid.
    This can be used to check that a configuration is valid before creating a plan.
    
    Failing GitHub checks will be added for any problems found.
    
    <p align="center">
        <img src="validate.png" width="1000">
    </p>
    
    If the $ProductName configuration is not valid, the build is failed.
    ''',
    meta_description='Validate a $ProductName configuration directory',
    inputs=[
        dataclasses.replace(path, description='The path to the $ProductName module to validate'),
        dataclasses.replace(workspace, description='''
          $ProductName workspace to use for the `terraform.workspace` value while validating. Note that for remote operations in a cloud backend, this is always `default`.

          Also used for discovering the $ProductName version to use, if not otherwise specified. 
          See [dflook/$ToolName-version](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-version#$ToolName-version-action) for details. 
        '''),
        dataclasses.replace(backend_config, description=backend_config.description + backend_reason),
        dataclasses.replace(backend_config_file, description=backend_config_file.description + backend_reason),
    ],
    outputs=[
        dataclasses.replace(failure_reason, description='''
            When the job outcome is `failure` because the validation failed, this will be set to 'validate-failed'.
            If the job fails for any other reason this will not be set.
            This can be used with the Actions expression syntax to conditionally run a step when the validate fails.
        ''')
    ],
    environment_variables=[
        GITHUB_DOT_COM_TOKEN,
        TERRAFORM_CLOUD_TOKENS,
        TERRAFORM_SSH_KEY,
        TERRAFORM_HTTP_CREDENTIALS,
        TERRAFORM_PRE_RUN,
    ],
    extra='''
## Example usage

This example workflow runs on every push and fails if the $ProductName
configuration is invalid.

```yaml
on: [push]

jobs:
  validate:
    runs-on: ubuntu-latest
    name: Validate $ProductName module
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName validate
        uses: dflook/$ToolName-validate@v1
        with:
          path: my-$ToolName-config
```

This example executes a run step only if the validation failed.

```yaml
on: [push]

jobs:
  validate:
    runs-on: ubuntu-latest
    name: Validate $ProductName module
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName validate
        uses: dflook/$ToolName-validate@v1
        id: validate
        with:
          path: my-$ToolName-config

      - name: Validate failed
        if: ${{ failure() && steps.validate.outputs.failure-reason == 'validate-failed' }}
        run: echo "$ToolName validate failed"
```
'''
)