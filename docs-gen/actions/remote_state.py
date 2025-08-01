import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.backend_type import backend_type
from inputs.workspace import workspace
from outputs.json_output_path import json_output_path
from outputs.terraform_outputs import terraform_outputs

remote_state = Action(
    'remote-state',
    '''
    Retrieves the root-level outputs from a $ProductName remote state.
    ''',
    inputs=[
        backend_type,
        dataclasses.replace(workspace, description='$ProductName workspace to get the outputs for'),
        backend_config,
        backend_config_file,
    ],
    outputs=[
        json_output_path,
        terraform_outputs
    ],
    environment_variables=[
        GITHUB_DOT_COM_TOKEN,
        dataclasses.replace(TERRAFORM_CLOUD_TOKENS, description='''
            API token for cloud hosts, of the form `<host>=<token>`. This will be used if the backed type is `remote`.
        ''')
    ],
    extra='''
## Example usage

This example sends a request to a url that has previously been provisioned by $ProductName, by fetching the url from the remote state in S3.

```yaml
name: Send request

on:
  push:
    branches:
      - main

env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

jobs:
  get_remote_state:
    runs-on: ubuntu-latest
    name: Run Test
    steps:
      - name: Get remote state
        uses: dflook/$ToolName-remote-state@v2
        id: remote-state
        with:
          backend_type: s3
          backend_config: |
            bucket=$ToolName-github-actions
            key=$ToolName-remote-state
            region=eu-west-2

      - name: Send request
        run: |
          curl "${{ steps.remote-state.outputs.url }}"
```
'''
)
