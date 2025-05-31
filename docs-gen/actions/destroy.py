import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from environment_variables.TERRAFORM_HTTP_CREDENTIALS import TERRAFORM_HTTP_CREDENTIALS
from environment_variables.TERRAFORM_PRE_RUN import TERRAFORM_PRE_RUN
from environment_variables.TERRAFORM_SSH_KEY import TERRAFORM_SSH_KEY
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.parallelism import parallelism
from inputs.path import path
from inputs.var_file import var_file
from inputs.var import var
from inputs.variables import variables
from inputs.workspace import workspace
from outputs.failure_reason import failure_reason
from outputs.lock_info import lock_info

destroy = Action(
    'destroy',
    '''
    :warning: This action uses the `$ToolName destroy` command to immediately destroy all resources in a $ProductName workspace.
    
    To generate a plan that can be reviewed you can instead use the [dflook/$ToolName-plan](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-plan)
    and [dflook/$ToolName-apply](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-plan) actions with the `destroy` input set to `true`.
    ''',
    meta_description='Destroys all resources in a $ProductName workspace',
    inputs=[
        path,
        dataclasses.replace(workspace, description='The name of the $ProductName workspace to destroy.'),
        dataclasses.replace(variables, description=variables.description.replace('plan', 'destroy')),
        var_file,
        var,
        backend_config,
        backend_config_file,
        parallelism
    ],
    outputs=[
        dataclasses.replace(failure_reason, description='''
          When the job outcome is `failure`, this output may be set. The value may be one of:

          - `destroy-failed` - The $ProductName destroy operation failed.
          - `state-locked` - The $ProductName state lock could not be obtained because it was already locked.

          If the job fails for any other reason this will not be set.
          This can be used with the Actions expression syntax to conditionally run a steps.
        '''),
        lock_info
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

This example destroys the resources in a workspace named after the git branch when the associated PR is closed.

```yaml
name: Cleanup

on:
  pull_request:
    types: [closed] 

jobs:
  destroy_workspace:
    runs-on: ubuntu-latest
    name: Destroy $ProductName workspace
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName destroy
        uses: dflook/$ToolName-destroy@v2
        with:
          path: my-$ToolName-config
          workspace: ${{ github.head_ref }}
```

This example retries the $ToolName destroy operation if it fails.

```yaml
name: Cleanup

on:
  pull_request:
    types: [closed]

jobs:
  destroy_workspace:
    runs-on: ubuntu-latest
    name: Destroy $ProductName workspace
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName destroy
        uses: dflook/$ToolName-destroy@v2
        id: first_try
        continue-on-error: true
        with:
          path: my-$ToolName-config
          workspace: ${{ github.head_ref }}

      - name: Retry failed destroy
        uses: dflook/$ToolName-destroy@v2
        if: ${{ steps.first_try.outputs.failure-reason == 'destroy-failed' }}
        with:
          path: my-$ToolName-config
          workspace: ${{ github.head_ref }}
```
'''
)
