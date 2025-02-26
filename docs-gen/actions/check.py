import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from environment_variables.TERRAFORM_HTTP_CREDENTIALS import TERRAFORM_HTTP_CREDENTIALS
from environment_variables.TERRAFORM_PRE_RUN import TERRAFORM_PRE_RUN
from environment_variables.TERRAFORM_SSH_KEY import TERRAFORM_SSH_KEY
from inputs.var import var
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.parallelism import parallelism
from inputs.path import path
from inputs.var_file import var_file
from inputs.variables import variables
from inputs.workspace import workspace
from outputs.failure_reason import failure_reason

check = Action(
    'check',
    '''
    Check for drift in $ProductName managed resources.
    This action runs the $ToolName plan command, and fails the build if any changes are required.
    This is intended to run on a schedule to notify if manual changes to your infrastructure have been made.
    ''',
    meta_description='Check if there are $ProductName changes to apply',
    inputs=[
        dataclasses.replace(path, description='Path to the $ProductName root module to check'),
        dataclasses.replace(workspace, description='$ProductName workspace to run the plan in'),
        variables,
        var_file,
        var,
        backend_config,
        backend_config_file,
        parallelism
    ],
    outputs=[
        dataclasses.replace(failure_reason, description='''
      When the job outcome is `failure` because the there are outstanding changes to apply, this will be set to 'changes-to-apply'.
      If the job fails for any other reason this will not be set.
      This can be used with the Actions expression syntax to conditionally run a step when there are changes to apply.
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
    
    This example workflow runs every morning and will fail if there has been
    unexpected changes to your infrastructure.
    
    ```yaml
    name: Check for infrastructure drift
    
    on:
      schedule:
        - cron:  "0 8 * * *"
    
    jobs:
      check_drift:
        runs-on: ubuntu-latest
        name: Check for drift of $ProductName configuration
        steps:
          - name: Checkout
            uses: actions/checkout@v4
    
          - name: Check
            uses: dflook/$ToolName-check@v1
            with:
              path: my-$ToolName-configuration
    ```
    
    This example executes a run step only if there are changes to apply.
    
    ```yaml
    name: Check for infrastructure drift
    
    on:
      schedule:
        - cron:  "0 8 * * *"
    
    jobs:
      check_drift:
        runs-on: ubuntu-latest
        name: Check for drift of $ProductName configuration
        steps:
          - name: Checkout
            uses: actions/checkout@v4
    
          - name: Check
            uses: dflook/$ToolName-check@v1
            id: check
            with:
              path: my-$ToolName-configuration
    
          - name: Changes detected
            if: ${{ failure() && steps.check.outputs.failure-reason == 'changes-to-apply' }}
            run: echo "There are outstanding changes to apply"
    ```
'''
)