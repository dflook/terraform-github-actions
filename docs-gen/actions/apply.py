import dataclasses

from action import Action
from environment_variables.GITHUB_DOT_COM_TOKEN import GITHUB_DOT_COM_TOKEN
from environment_variables.GITHUB_TOKEN import GITHUB_TOKEN
from environment_variables.TERRAFORM_ACTIONS_GITHUB_TOKEN import TERRAFORM_ACTIONS_GITHUB_TOKEN
from environment_variables.TERRAFORM_CLOUD_TOKENS import TERRAFORM_CLOUD_TOKENS
from environment_variables.TERRAFORM_HTTP_CREDENTIALS import TERRAFORM_HTTP_CREDENTIALS
from environment_variables.TERRAFORM_PRE_RUN import TERRAFORM_PRE_RUN
from environment_variables.TERRAFORM_SSH_KEY import TERRAFORM_SSH_KEY
from inputs.auto_approve import auto_approve
from inputs.backend_config import backend_config
from inputs.backend_config_file import backend_config_file
from inputs.destroy import destroy
from inputs.label import label
from inputs.parallelism import parallelism
from inputs.path import path
from inputs.plan_path import plan_path as plan_path_input
from inputs.replace import replace
from inputs.target import target
from inputs.var_file import var_file
from inputs.variables import variables
from inputs.var import var
from inputs.workspace import workspace
from outputs.failure_reason import failure_reason
from outputs.json_plan_path import json_plan_path
from outputs.lock_info import lock_info
from outputs.run_id import run_id
from outputs.terraform_outputs import terraform_outputs
from outputs.text_plan_path import text_plan_path

apply = Action(
    'apply',
    '''
This action applies a $ProductName plan.
The default behaviour is to apply the plan that has been added to a PR using the [`dflook/$ToolName-plan`](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-plan) action.

If the plan is not found or has changed, then the `apply` action will fail.
This is to ensure that the action only applies changes that have been reviewed by a human.

You can instead set `auto_approve: true` which will generate a plan and apply it immediately, without looking for a plan attached to a PR.

## Demo
This a demo of the process for apply a $ProductName change using the [`dflook/$ToolName-plan`](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-plan) and [`dflook/$ToolName-apply`](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-apply) actions.

<p align="center">
    <img src="planapply.gif" width="1000">
</p>

## GitHub

To make best use of this action, require that the plan is always reviewed
before merging the PR to approve. You can enforce this in github by
going to the branch settings for the repo and enable protection for
the main branch:

1. Enable 'Require pull request reviews before merging'
2. Check 'Dismiss stale pull request approvals when new commits are pushed'
3. Enable 'Require status checks to pass before merging', and select the job that runs the plan.
4. Enable 'Require branches to be up to date before merging'
''',
    meta_description='Apply a $ProductName plan',
    inputs_intro='''
These input values must be the same as any [`dflook/$ToolName-plan`](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-plan) for the same configuration. (unless auto_approve: true)
    ''',
    inputs=[
        dataclasses.replace(path, description="Path to the $ProductName root module to apply"),
        dataclasses.replace(workspace, description="$ProductName workspace to run the apply in"),
        dataclasses.replace(label, description=label.description + "\nIt must be the same as the `label` used in the corresponding [`dflook/$ToolName-plan`](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-plan) action."),
        variables,
        var_file,
        var,
        backend_config,
        backend_config_file,
        replace,
        dataclasses.replace(target, description='''
  List of resources to apply, one per line.
  The apply operation will be limited to these resources and their dependencies.
        '''),
        dataclasses.replace(destroy, description='''
Set to `true` to destroy all resources.

This generates and applies a plan in [destroy mode]($DestroyModeUrl).'''),
        plan_path_input,
        auto_approve,
        parallelism
    ],
    outputs=[
        dataclasses.replace(json_plan_path, description=json_plan_path.description + "\nThis won't be set if the backend type is `remote` - $ProductName does not support saving remote plans."),
        dataclasses.replace(text_plan_path, description=text_plan_path.description + "This won't be set if `auto_approve` is true while using a `remote` backend."),
        dataclasses.replace(failure_reason, description='''
  When the job outcome is `failure`, this output may be set. The value may be one of:

  - `apply-failed` - The Terraform apply operation failed.
  - `plan-changed` - The approved plan is no longer accurate, so the apply will not be attempted.
  - `state-locked` - The Terraform state lock could not be obtained because it was already locked. 

  If the job fails for any other reason this will not be set.
  This can be used with the Actions expression syntax to conditionally run steps.
        '''
        ),
        lock_info,
        run_id,
        terraform_outputs
    ],
    environment_variables=[
        dataclasses.replace(GITHUB_TOKEN, description='''
The GitHub authorization token to use to fetch an approved plan from a PR. 
This must belong to the same user/app as the token used by the [$ToolName-plan](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-plan) action.
        ''' + GITHUB_TOKEN.description),
        TERRAFORM_ACTIONS_GITHUB_TOKEN,
        GITHUB_DOT_COM_TOKEN,
        TERRAFORM_CLOUD_TOKENS,
        TERRAFORM_SSH_KEY,
        TERRAFORM_HTTP_CREDENTIALS,
        TERRAFORM_PRE_RUN,
    ],
    extra='''
## Workflow events

When applying a plan from a PR comment (`auto_approve` is the default of `false`), the workflow can be triggered by the following events:

  - pull_request
  - pull_request_review_comment
  - pull_request_target
  - pull_request_review
  - issue_comment, if the comment is on a PR (see below)
  - push, if the pushed commit came from a PR (see below)
  - repository_dispatch, if the client payload includes the pull_request url (see below)

When `auto_approve` is set to `true`, the workflow can be triggered by any event.

### issue_comment

This event triggers workflows when a comment is made in a Issue or a Pull Request.
Since running the action will only work in the context of a PR, the workflow should check that the comment is on a PR before running.

Also take care to checkout the PR ref.

```yaml
jobs:
  apply:
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
        uses: dflook/$ToolName-apply@v1
        with:
          path: my-$ToolName-config
```

### push

The pushed commit must have come from a Pull Request. Typically this is used to trigger a workflow that runs on the main branch after a PR has been merged.

### repository_dispatch

This event can be used to trigger a workflow from another workflow. The client payload must include the pull_request api url of where the plan PR comment can be found.

A minimal example payload looks like:
```json
{
  "pull_request": {
    "url": "https://api.github.com/repos/dflook/terraform-github-actions/pulls/1"
  }
}
```

## Example usage

### Apply PR approved plans

This example workflow runs for every push to main. If the commit
came from a PR that has been merged, applies the plan from the PR.

```yaml
name: Apply

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pull-requests: write

jobs:
  apply:
    runs-on: ubuntu-latest
    name: Apply approved plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName apply
        uses: dflook/$ToolName-apply@v1
        with:
          path: my-$ToolName-config
```

### Always apply changes

This example workflow runs for every push to main.
Changes are planned and applied.

```yaml
name: Apply

on:
  push:
    branches:
      - main

jobs:
  apply:
    runs-on: ubuntu-latest
    name: Apply $ProductName
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName apply
        uses: dflook/$ToolName-apply@v1
        with:
          path: my-$ToolName-config
          auto_approve: true
```

### Apply specific resources

This example workflow runs every morning and updates a TLS certificate
if necessary.

```yaml
name: Rotate certs

on:
  schedule:
    - cron:  "0 8 * * *"

jobs:
  apply:
    runs-on: ubuntu-latest
    name: Rotate certs
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName apply
        uses: dflook/$ToolName-apply@v1
        with:
          path: my-$ToolName-config
          auto_approve: true
          target: |
            kubernetes_secret.tls_cert_public
            kubernetes_secret.tls_cert_private
```

### Applying a plan using a comment

This workflow applies a plan on demand, triggered by someone
commenting `$ToolName apply` on the PR. The plan is taken
from an existing comment generated by the [`dflook/$ToolName-plan`](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-plan)
action.

```yaml
name: $ProductName Apply

on: [issue_comment]

jobs:
  apply:
    if: ${{ github.event.issue.pull_request && contains(github.event.comment.body, '$ToolName apply') }}
    runs-on: ubuntu-latest
    name: Apply $ProductName plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          ref: refs/pull/${{ github.event.issue.number }}/merge

      - name: $ProductName apply
        uses: dflook/$ToolName-apply@v1
        with:
          path: my-$ToolName-config
```

This example retries the $ToolName apply operation if it fails.

```yaml
name: Apply plan

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pull-requests: write

jobs:
  plan:
    runs-on: ubuntu-latest
    name: Apply $ProductName plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: $ToolName apply
        uses: dflook/$ToolName-apply@v1
        continue-on-error: true
        id: first_try
        with:
          path: $ToolName

      - name: Retry failed apply
        uses: dflook/$ToolName-apply@v1
        if: ${{ steps.first_try.outputs.failure-reason == 'apply-failed' }}
        with:
          path: $ToolName
          auto_approve: true
```
'''
)