import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_ACTIONS_GITHUB_TOKEN import TERRAFORM_ACTIONS_GITHUB_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from environment_variables.TERRAFORM_HTTP_CREDENTIALS import TERRAFORM_HTTP_CREDENTIALS
from environment_variables.TERRAFORM_PRE_RUN import TERRAFORM_PRE_RUN
from environment_variables.TERRAFORM_SSH_KEY import TERRAFORM_SSH_KEY
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.path import path
from inputs.workspace import workspace

new_workspace = Action(
    'new-workspace',
    '''
    Creates a new $ProductName workspace. If the workspace already exists, succeeds without doing anything.
    ''',
    inputs=[
        path,
        dataclasses.replace(workspace, description='The name of the $ProductName workspace to create.', required=True, default=None),
        backend_config,
        backend_config_file,
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

This example creates a workspace named after the git branch when the
associated PR is opened or updated, and deploys a test environment to it.

```yaml
name: Run integration tests

on: [pull_request]

jobs:
  integration:
    runs-on: ubuntu-latest
    name: Run integration tests
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Use branch workspace
        uses: dflook/$ToolName-new-workspace@v1
        with:
          path: $ToolName
          workspace: ${{ github.head_ref }}

      - name: Deploy test infrastrucutre
        uses: dflook/$ToolName-apply@v1
        with:
          path: $ToolName
          workspace: ${{ github.head_ref }}
          auto_approve: true
```
'''
)