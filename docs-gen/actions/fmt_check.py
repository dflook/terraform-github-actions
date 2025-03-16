import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.path import path
from inputs.workspace import workspace
from outputs.failure_reason import failure_reason

fmt_check = Action(
    'fmt-check',
    '''
    This action uses the `$ToolName fmt` command to check that all files in a $ProductName configuration directory are in the canonical format.
    This can be used to check that files are properly formatted before merging.
    
    If any files are not correctly formatted a failing GitHub check will be added for the file, and the job failed.
    ''',
    meta_description='Check that OpenTofu configuration files are in canonical format',
    inputs=[
        dataclasses.replace(path, description='The path containing $ProductName files to check the formatting of.'),
        dataclasses.replace(workspace, description='''
            $ProductName workspace to inspect when discovering the $ProductName version to use, if the version is not otherwise specified.
            See [dflook/$ToolName-version](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-version#$ToolName-version-action) for details.
        '''),
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
    outputs=[
        dataclasses.replace(failure_reason, description='''
          When the job outcome is `failure` because the format check failed, this will be set to 'check-failed'.
          If the job fails for any other reason this will not be set.
          This can be used with the Actions expression syntax to conditionally run a step when the format check fails.
        ''')
    ],
    environment_variables=[
        GITHUB_DOT_COM_TOKEN,
        dataclasses.replace(TERRAFORM_CLOUD_TOKENS, description='For the purpose of detecting the $ProductName version to use from a cloud backend.' + TERRAFORM_CLOUD_TOKENS.description),
    ],
    extra='''
## Example usage

This example workflow runs on every push and fails if any of the
$ProductName files are not formatted correctly.

```yaml
name: Check file formatting

on: [push]

jobs:
  check_format:
    runs-on: ubuntu-latest
    name: Check $ProductName file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName fmt
        uses: dflook/$ToolName-fmt-check@v1
        with:
          path: my-$ToolName-config
```

This example executes a run step only if the format check failed.

```yaml
name: Check file formatting

on: [push]

jobs:
  check_format:
    runs-on: ubuntu-latest
    name: Check $ProductName file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName fmt
        uses: dflook/$ToolName-fmt-check@v1
        id: fmt-check
        with:
          path: my-$ToolName-config

      - name: Wrong formatting found
        if: ${{ failure() && steps.fmt-check.outputs.failure-reason == 'check-failed' }}
        run: echo "formatting check failed"
```
'''
)