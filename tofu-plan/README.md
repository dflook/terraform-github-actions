# tofu-plan action

This is one of a suite of OpenTofu related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This actions generates an OpenTofu plan.
If the triggering event relates to a PR it will add a comment on the PR containing the generated plan.

<p align="center">
    <img src="plan.png" width="600">
</p>

The `GITHUB_TOKEN` environment variable must be set for the PR comment to be added.
The action can be run on other events, which prints the plan to the workflow log.

The [dflook/tofu-apply](https://github.com/dflook/terraform-github-actions/tree/main/tofu-apply) action can be used to apply the generated plan.

## Inputs

* `path`

  Path to the OpenTofu root module to apply

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  OpenTofu workspace to run the plan for

  - Type: string
  - Optional
  - Default: `default`

* `label`

  A friendly name for the environment the OpenTofu configuration is for.
  This will be used in the PR comment for easy identification.

  If set, must be the same as the `label` used in the corresponding `tofu-apply` command.

  - Type: string
  - Optional

* `variables`

  Variables to set for the tofu plan. This should be valid OpenTofu syntax - like a [variable definition file](https://www.terraform.io/docs/language/values/variables.html#variable-definitions-tfvars-files).

  ```yaml
  with:
    variables: |
      image_id = "${{ secrets.AMI_ID }}"
      availability_zone_names = [
        "us-east-1a",
        "us-west-1c",
      ]
  ```

  Variables set here override any given in `var_file`s.

  - Type: string
  - Optional

* `var_file`

  List of tfvars files to use, one per line.
  Paths should be relative to the GitHub Actions workspace
  
  ```yaml
  with:
    var_file: |
      common.tfvars
      prod.tfvars
  ```

  - Type: string
  - Optional

* `backend_config`

  List of OpenTofu backend config values, one per line.

  ```yaml
  with:
    backend_config: token=${{ secrets.BACKEND_TOKEN }}
  ```

  - Type: string
  - Optional

* `backend_config_file`

  List of OpenTofu backend config files to use, one per line.
  Paths should be relative to the GitHub Actions workspace

  ```yaml
  with:
    backend_config_file: prod.backend.tfvars
  ```

  - Type: string
  - Optional

* `replace`

  List of resources to replace, one per line.

  ```yaml
  with:
    replace: |
      random_password.database
  ```

  - Type: string
  - Optional

* `target`

  List of resources to apply, one per line.
  The plan will be limited to these resources and their dependencies.

  ```yaml
  with:
    target: |
      kubernetes_secret.tls_cert_public
      kubernetes_secret.tls_cert_private
  ```

  - Type: string
  - Optional

* `destroy`

  Set to `true` to generate a plan to destroy all resources.

  This generates a plan in [destroy mode](https://developer.hashicorp.com/terraform/cli/commands/plan#planning-modes).

  - Type: boolean
  - Optional
  - Default: false

* `add_github_comment`

  Controls whether a comment is added to the PR with the generated plan.

  The default is `true`, which adds a comment to the PR with the results of the plan.
  Set to `changes-only` to add a comment only when the plan indicates there are changes to apply.
  Set to `always-new` to always create a new comment for each plan, instead of updating the previous comment.
  Set to `false` to disable the comment - the plan will still appear in the workflow log.

  - Type: string
  - Optional
  - Default: true

* `parallelism`

  Limit the number of concurrent operations

  - Type: number
  - Optional
  - Default: The tofu default (10)

## Environment Variables

* `GITHUB_TOKEN`

  The GitHub authorization token to use to create comments on a PR.
  The token provided by GitHub Actions can be used - it can be passed by
  using the `${{ secrets.GITHUB_TOKEN }}` expression, e.g.

  ```yaml
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```

  The token provided by GitHub Actions has default permissions at GitHub's whim. You can see what it is for your repo under the repo settings.

  The minimum permissions are `pull-requests: write`.
  It will also likely need `contents: read` so the job can checkout the repo.

  You can also use any other App token that has `pull-requests: write` permission.

  You can use a fine-grained Personal Access Token which has repository permissions:
  - Read access to metadata
  - Read and Write access to pull requests

  You can also use a classic Personal Access Token which has the `repo` scope.

  The GitHub user or app that owns the token will be the PR comment author.

  - Type: string
  - Optional

* `TERRAFORM_ACTIONS_GITHUB_TOKEN`

  When this is set it is used instead of `GITHUB_TOKEN`, with the same behaviour.
  The GitHub OpenTofu provider also uses the `GITHUB_TOKEN` environment variable, 
  so this can be used to make the github actions and the OpenTofu provider use different tokens.

  - Type: string
  - Optional

* `TERRAFORM_CLOUD_TOKENS`

  API tokens for cloud hosts, of the form `<host>=<token>`. Multiple tokens may be specified, one per line.
  These tokens may be used with the `remote` backend and for fetching required modules from the registry.

  e.g:
  ```yaml
  env:
    TERRAFORM_CLOUD_TOKENS: app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
  ```

  With other registries:
  ```yaml
  env:
    TERRAFORM_CLOUD_TOKENS: |
      app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
      tofu.example.com=${{ secrets.TF_REGISTRY_TOKEN }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_SSH_KEY`

  A SSH private key that OpenTofu will use to fetch git/mercurial module sources.

  This should be in PEM format.

  For example:
  ```yaml
  env:
    TERRAFORM_SSH_KEY: ${{ secrets.TERRAFORM_SSH_KEY }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_HTTP_CREDENTIALS`

  Credentials that will be used for fetching modules sources with `git::http://`, `git::https://`, `http://` & `https://` schemes.

  Credentials have the format `<host>=<username>:<password>`. Multiple credentials may be specified, one per line.

  Each credential is evaluated in order, and the first matching credentials are used. 

  Credentials that are used by git (`git::http://`, `git::https://`) allow a path after the hostname.
  Paths are ignored by `http://` & `https://` schemes.
  For git module sources, a credential matches if each mentioned path segment is an exact match.

  For example:
  ```yaml
  env:
    TERRAFORM_HTTP_CREDENTIALS: |
      example.com=dflook:${{ secrets.HTTPS_PASSWORD }}
      github.com/dflook/terraform-github-actions.git=dflook-actions:${{ secrets.ACTIONS_PAT }}
      github.com/dflook=dflook:${{ secrets.DFLOOK_PAT }}
      github.com=graham:${{ secrets.GITHUB_PAT }}  
  ```

  - Type: string
  - Optional

* `TF_PLAN_COLLAPSE_LENGTH`

  When PR comments are enabled, the tofu output is included in a collapsable pane.
  
  If a tofu plan has fewer lines than this value, the pane is expanded
  by default when the comment is displayed.

  ```yaml
  env:
    TF_PLAN_COLLAPSE_LENGTH: 30
  ```

  - Type: integer
  - Optional
  - Default: 10

* `TERRAFORM_PRE_RUN`

  A set of commands that will be ran prior to `tofu init`. This can be used to customise the environment before running OpenTofu. 
  
  The runtime environment for these actions is subject to change in minor version releases. If using this environment variable, specify the minor version of the action to use.
  
  The runtime image is currently based on `debian:bullseye`, with the command run using `bash -xeo pipefail`.

  For example:
  ```yaml
  env:
    TERRAFORM_PRE_RUN: |
      # Install latest Azure CLI
      curl -skL https://aka.ms/InstallAzureCLIDeb | bash
      
      # Install postgres client
      apt-get install -y --no-install-recommends postgresql-client
  ```

  - Type: string
  - Optional

## Outputs

* `changes`

  Set to 'true' if the plan would apply any changes, 'false' if it wouldn't.

  - Type: boolean

* `plan_path`

  This is the path to the generated plan in an opaque binary format.
  The path is relative to the Actions workspace.

  The plan can be used as the `plan_file` input to the [dflook/tofu-apply](https://github.com/dflook/terraform-github-actions/tree/main/tofu-apply) action.

  OpenTofu plans often contain sensitive information, so this output should be treated with care.

  - Type: string

* `json_plan_path`

  This is the path to the generated plan in [JSON Output Format](https://www.terraform.io/docs/internals/json-format.html)
  The path is relative to the Actions workspace.

  OpenTofu plans often contain sensitive information, so this output should be treated with care.

  - Type: string

* `text_plan_path`

  This is the path to the generated plan in a human-readable format.
  The path is relative to the Actions workspace.

  - Type: string

* `to_add`
* `to_change`
* `to_destroy`
* `to_move`
* `to_import`

  The number of resources that would be affected by each type of operation.

  - Type: number

* `run_id`

  If the root module uses the `remote` or `cloud` backend in remote execution mode, this output will be set to the remote run id.

  - Type: string

## Workflow events

When adding the plan to a PR comment (`add_github_comment` is not `false`), the workflow can be triggered by the following events:

  - pull_request
  - pull_request_review_comment
  - pull_request_target
  - pull_request_review
  - issue_comment, if the comment is on a PR (see below)
  - push, if the pushed commit came from a PR (see below)
  - repository_dispatch, if the client payload includes the pull_request url (see below)

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
        uses: actions/checkout@v3
        with:
          ref: refs/pull/${{ github.event.issue.number }}/merge

      - name: tofu apply
        uses: dflook/tofu-plan@v1
        with:
          path: my-terraform-config
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
and create or updates a comment with the tofu plan

```yaml
name: PR Plan

on: [pull_request]

permissions:
  contents: read
  pull-requests: write

jobs:
  plan:
    runs-on: ubuntu-latest
    name: Create tofu plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}            
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: tofu plan
        uses: dflook/tofu-plan@v1
        with:
          path: my-terraform-config
```

### A full example of inputs

This example workflow demonstrates most of the available inputs:
- The environment variables are set at the workflow level.
- The PR comment will be labelled `production`, and the plan will use the `prod` workspace.
- Variables are read from `env/prod.tfvars`, with `turbo_mode` overridden to `true`.
- The backend config is taken from `env/prod.backend`, and the token is set from a secret.

```yaml
name: PR Plan

on: [pull_request]

env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  TERRAFORM_CLOUD_TOKENS: tofu.example.com=${{ secrets.TF_REGISTRY_TOKEN }}
  TERRAFORM_SSH_KEY: ${{ secrets.TERRAFORM_SSH_KEY }}

permissions:
  contents: read
  pull-requests: write

jobs:
  plan:
    runs-on: ubuntu-latest
    name: Create OpenTofu plan
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: tofu plan
        uses: dflook/tofu-plan@v1
        with:
          path: my-terraform-config
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
commenting `tofu plan` on the PR. The action will create or update
a comment on the PR with the generated plan.

```yaml
name: OpenTofu Plan

on: [issue_comment]

permissions:
  contents: read
  pull-requests: write

jobs:
  plan:
    if: ${{ github.event.issue.pull_request && contains(github.event.comment.body, 'tofu plan') }}
    runs-on: ubuntu-latest
    name: Create OpenTofu plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          ref: refs/pull/${{ github.event.issue.number }}/merge

      - name: tofu plan
        uses: dflook/tofu-plan@v1
        with:
          path: my-terraform-config
```
