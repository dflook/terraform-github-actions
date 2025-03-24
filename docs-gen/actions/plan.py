import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.GITHUB_TOKEN import GITHUB_TOKEN
from environment_variables.TERRAFORM_ACTIONS_GITHUB_TOKEN import TERRAFORM_ACTIONS_GITHUB_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from environment_variables.TERRAFORM_HTTP_CREDENTIALS import TERRAFORM_HTTP_CREDENTIALS
from environment_variables.TERRAFORM_PRE_RUN import TERRAFORM_PRE_RUN
from environment_variables.TERRAFORM_SSH_KEY import TERRAFORM_SSH_KEY
from environment_variables.TF_PLAN_COLLAPSE_LENGTH import TF_PLAN_COLLAPSE_LENGTH
from inputs.add_github_comment import add_github_comment
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.destroy import destroy
from inputs.label import label
from inputs.parallelism import parallelism
from inputs.path import path
from inputs.refresh import refresh
from inputs.replace import replace
from inputs.target import target
from inputs.var import var
from inputs.var_file import var_file
from inputs.variables import variables
from inputs.workspace import workspace
from outputs.changes import changes
from outputs.json_plan_path import json_plan_path
from outputs.plan_path import plan_path
from outputs.run_id import run_id
from outputs.text_plan_path import text_plan_path
from outputs.to_add import to_add

plan = Action(
    'plan',
    '''
This action generates a $ProductName plan.
If the triggering event relates to a PR it will add a comment on the PR containing the generated plan.

<p align="center">
    <img src="plan.png" width="600" alt="An example of a PR comment created by the action">
</p>

The `GITHUB_TOKEN` environment variable must be set for the PR comment to be added.
The action can be run on other events, which prints the plan to the workflow log.

The [dflook/$ToolName-apply](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-apply) action can be used to apply the generated plan.
''',
    meta_description='Create a $ProductName plan',
    inputs=[
        dataclasses.replace(path, description="The path to the $ProductName root module to generate a plan for."),
        dataclasses.replace(workspace, description='$ProductName workspace to run the plan for.'),
        dataclasses.replace(label, description=label.description + "\nIf this is set, it must be the same as the `label` used in any corresponding [`dflook/$ToolName-apply`](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-apply) action."),
        variables,
        var_file,
        var,
        backend_config,
        backend_config_file,
        replace,
        target,
        destroy,
        refresh,
        add_github_comment,
        parallelism
    ],
    outputs=[
        changes,
        plan_path,
        json_plan_path,
        text_plan_path,
        to_add,
        run_id
    ],
    environment_variables=[
        dataclasses.replace(GITHUB_TOKEN, description='''
The GitHub authorization token to use to create comments on a PR.
''' + GITHUB_TOKEN.description + '''
The GitHub user or app that owns the token will be the PR comment author.
'''),
        TERRAFORM_ACTIONS_GITHUB_TOKEN,
        GITHUB_DOT_COM_TOKEN,
        TERRAFORM_CLOUD_TOKENS,
        TERRAFORM_SSH_KEY,
        TERRAFORM_HTTP_CREDENTIALS,
        TF_PLAN_COLLAPSE_LENGTH,
        TERRAFORM_PRE_RUN,
    ],
    extra='''
## Workflow events

When adding the plan to a PR comment (`add_github_comment` is not `false`), the workflow can be triggered by the following events:

* pull_request
* pull_request_review_comment
* pull_request_target
* pull_request_review
* issue_comment, if the comment is on a PR (see below)
* push, if the pushed commit came from a PR (see below)
* repository_dispatch, if the client payload includes the pull_request url (see below)

When `add_github_comment` is set to `false`, the workflow can be triggered by any event.

### issue_comment

This event triggers workflows when a comment is made in a Issue, as well as a Pull Request.
Since running the action will only work in the context of a PR, the workflow should check that the comment is on a PR before running.

Also take care to checkout the PR ref.

```yaml
jobs:
  plan:
    if: ${{ github.event.issue.pull_request }}
    runs-on: ubuntu-latest
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          ref: refs/pull/${{ github.event.issue.number }}/merge

      - name: $ToolName apply
        uses: dflook/$ToolName-plan@v1
        with:
          path: my-$ToolName-config
```

### push

The pushed commit must have come from a Pull Request. Typically this is used to trigger a workflow that runs on the main branch after a PR has been merged.

### repository_dispatch

This event can be used to trigger a workflow from another workflow. The client payload must include the pull_request api url of where the plan PR comment should be added.

A minimal example payload looks like:

```json
{
  "pull_request": {
    "url": "https://api.github.com/repos/dflook/terraform-github-actions/pulls/1"
  }
}
```

## Example usage

### Automatically generating a plan

This example workflow runs on every push to an open pull request,
and create or updates a comment with the $ToolName plan

```yaml
name: PR Plan

on: [pull_request]

permissions:
  contents: read
  pull-requests: write

jobs:
  plan:
    runs-on: ubuntu-latest
    name: Create $ToolName plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}            
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName plan
        uses: dflook/$ToolName-plan@v1
        with:
          path: my-$ToolName-config
```

### A full example of inputs

This example workflow demonstrates most of the available inputs:

* The environment variables are set at the workflow level.
* The PR comment will be labelled `production`, and the plan will use the `prod` workspace.
* Variables are read from `env/prod.tfvars`, with `turbo_mode` overridden to `true`.
* The backend config is taken from `env/prod.backend`, and the token is set from a secret.

```yaml
name: PR Plan

on: [pull_request]

env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  TERRAFORM_CLOUD_TOKENS: $ToolName.example.com=${{ secrets.TF_REGISTRY_TOKEN }}
  TERRAFORM_SSH_KEY: ${{ secrets.TERRAFORM_SSH_KEY }}

permissions:
  contents: read
  pull-requests: write

jobs:
  plan:
    runs-on: ubuntu-latest
    name: Create $ProductName plan
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName plan
        uses: dflook/$ToolName-plan@v1
        with:
          path: my-$ToolName-config
          label: production
          workspace: prod
          var_file: env/prod.tfvars
          variables: |
            turbo_mode=true
          backend_config_file: env/prod.backend
          backend_config: token=${{ secrets.BACKEND_TOKEN }}
```

### Generating a plan using a comment

This workflow generates a plan on demand, triggered by someone
commenting `$ToolName plan` on the PR. The action will create or update
a comment on the PR with the generated plan.

```yaml
name: $ProductName Plan

on: [issue_comment]

permissions:
  contents: read
  pull-requests: write

jobs:
  plan:
    if: ${{ github.event.issue.pull_request && contains(github.event.comment.body, '$ToolName plan') }}
    runs-on: ubuntu-latest
    name: Create $ProductName plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          ref: refs/pull/${{ github.event.issue.number }}/merge

      - name: $ToolName plan
        uses: dflook/$ToolName-plan@v1
        with:
          path: my-$ToolName-config
```
'''
)
