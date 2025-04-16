import dataclasses

from action import Action, OpenTofu
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.path import path
from inputs.var_file import var_file
from inputs.variables import variables
from inputs.workspace import workspace

fmt = Action(
    'fmt',
    '''
    This action uses the `$ToolName fmt -recursive` command to reformat files in a directory into a canonical format.
    ''',
    meta_description='Rewrite $ProductName files into canonical format',
    inputs=[
        dataclasses.replace(path, description='The path containing $ProductName files to format.'),
        dataclasses.replace(workspace, description='''
            $ProductName workspace to inspect when discovering the $ProductName version to use, if the version is not otherwise specified.
            See [dflook/$ToolName-version](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-version#$ToolName-version-action) for details.
        '''),
        dataclasses.replace(variables, available_in=[OpenTofu], description='''
            Variables to set when initializing $ProductName. This should be valid $ProductName syntax - like a [variable definition file]($VariableDefinitionUrl).
            Variables set here override any given in `var_file`s.
        '''),
        dataclasses.replace(var_file, available_in=[OpenTofu]),
        dataclasses.replace(backend_config, description='''
            List of $ProductName backend config values, one per line. This is used for discovering the $ProductName version to use, if the version is not otherwise specified.
            See [dflook/$ToolName-version](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-version#$ToolName-version-action) for details.
        '''),
        dataclasses.replace(backend_config_file, description='''
            List of $ProductName backend config files to use, one per line. This is used for discovering the $ProductName version to use, if the version is not otherwise specified.
            See [dflook/$ToolName-version](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-version#$ToolName-version-action) for details.
            Paths should be relative to the GitHub Actions workspace
        ''')
    ],
    environment_variables=[
        GITHUB_DOT_COM_TOKEN,
        dataclasses.replace(TERRAFORM_CLOUD_TOKENS, description='For the purpose of detecting the $ProductName version to use from a cloud backend.' + TERRAFORM_CLOUD_TOKENS.description),
    ],
    extra='''
## Example usage

This example automatically creates a pull request to fix any formatting
problems that get merged into the main branch.

```yaml
name: Fix $ProductName file formatting

on:
  push:
    branches:
      - main

jobs:
  format:
    runs-on: ubuntu-latest
    name: Check $ProductName file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName fmt
        uses: dflook/$ToolName-fmt@v1
        with:
          path: my-$ToolName-config

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: $ToolName fmt
          title: Reformat $ToolName files
          body: Update $ProductName files to canonical format using `$ToolName fmt`
          branch: automated-$ToolName-fmt
```
'''
)
