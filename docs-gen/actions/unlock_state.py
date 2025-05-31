import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from environment_variables.TERRAFORM_HTTP_CREDENTIALS import TERRAFORM_HTTP_CREDENTIALS
from environment_variables.TERRAFORM_PRE_RUN import TERRAFORM_PRE_RUN
from environment_variables.TERRAFORM_SSH_KEY import TERRAFORM_SSH_KEY
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.lock_id import lock_id
from inputs.path import path
from inputs.workspace import workspace

unlock_state = Action(
    'unlock-state',
    '''
    Force unlocks a $ProductName remote state.
    ''',
    inputs=[
        dataclasses.replace(path, description='Path to the $ProductName root module that defines the remote state to unlock'),
        dataclasses.replace(workspace, description='$ProductName workspace to unlock the remote state for'),
        backend_config,
        backend_config_file,
        lock_id
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
name: "Unlock state"
on:
  workflow_dispatch:
    inputs:
      path:
        description: "Path to the $ProductName root module"
        required: true
      lock_id:
        description: "Lock ID to be unlocked"
        required: true

env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

jobs:
  unlock:
    name: Unlock
    runs-on: ubuntu-latest
    steps:
      - name: Checkout current branch
        uses: actions/checkout@v4

      - name: $ProductName Unlock
        uses: dflook/$ToolName-unlock-state@v2
        with:
          path: ${{ github.event.inputs.path }}
          lock_id: ${{ github.event.inputs.lock_id }}
```
'''
)
