# terraform-refresh action

This is one of a suite of Terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This actions runs a Terraform apply operation in refresh-only mode.
This will synchronise the Terraform state with the actual resources, but will not make any changes to the resources.

## Inputs

These input values must be the same as any [`dflook/terraform-plan`](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan) for the same configuration. (unless auto_approve: true)

* `path`

  Path to the Terraform root module to apply

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  Terraform workspace to run the apply in

  - Type: string
  - Optional
  - Default: `default`

* `backend_config`

  List of Terraform backend config values, one per line.

  ```yaml
  with:
    backend_config: token=${{ secrets.BACKEND_TOKEN }}
  ```

  - Type: string
  - Optional

* `backend_config_file`

  List of Terraform backend config files to use, one per line.
  Paths should be relative to the GitHub Actions workspace

  ```yaml
  with:
    backend_config_file: prod.backend.tfvars
  ```

  - Type: string
  - Optional

## Outputs

* `failure-reason`

  When the job outcome is `failure`, this output may be set. The value may be one of:

  - `apply-failed` - The Terraform apply operation failed.
  - `plan-changed` - The approved plan is no longer accurate, so the apply will not be attempted.
  - `state-locked` - The Terraform state lock could not be obtained because it was already locked. 

  If the job fails for any other reason this will not be set.
  This can be used with the Actions expression syntax to conditionally run steps.

* `lock-info`

  When the job outcome is `failure` and the failure-reason is `state-locked`, this output will be set.

  It is a json object containing any available state lock information and typically has the form:
  ```json
  {
    "ID": "838fbfde-c5cd-297f-84a4-d7578b4a4880",
    "Path": "terraform-github-actions/test-unlock-state",
    "Operation": "OperationTypeApply",
    "Who": "root@e9d43b0c6478",
    "Version": "1.3.7",
    "Created": "2023-01-28 00:16:41.560904373 +0000 UTC",
    "Info": ""
  }
  ```

* `run_id`

  If the root module uses the `remote` or `cloud` backend in remote execution mode, this output will be set to the remote run id.

  - Type: string

## Environment Variables

* `GITHUB_DOT_COM_TOKEN`

  This is used to specify a token for GitHub.com when the action is running on a GitHub Enterprise instance.
  This is only used for downloading OpenTofu binaries from GitHub.com.
  If this is not set, an unauthenticated request will be made to GitHub.com to download the binary, which may be rate limited.

  - Type: string
  - Optional

* `TERRAFORM_CLOUD_TOKENS`

  API tokens for cloud hosts, of the form `<host>=<token>`. Multiple tokens may be specified, one per line.
  These tokens may be used with the `remote` backend or `cloud` blocks in the configuration.

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
      terraform.example.com=${{ secrets.TF_REGISTRY_TOKEN }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_SSH_KEY`

  A SSH private key that Terraform will use to fetch git module sources.

  This should be in PEM format.

  For example:
  ```yaml
  env:
    TERRAFORM_SSH_KEY: ${{ secrets.TERRAFORM_SSH_KEY }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_PRE_RUN`

  A set of commands that will be ran prior to `terraform init`. This can be used to customise the environment before running Terraform. 
  
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

      - name: terraform apply
        uses: dflook/terraform-apply@v1
        with:
          path: my-terraform-config
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

      - name: terraform apply
        uses: dflook/terraform-apply@v1
        with:
          path: my-terraform-config
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
    name: Apply Terraform
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: terraform apply
        uses: dflook/terraform-apply@v1
        with:
          path: my-terraform-config
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

      - name: terraform apply
        uses: dflook/terraform-apply@v1
        with:
          path: my-terraform-config
          auto_approve: true
          target: |
            kubernetes_secret.tls_cert_public
            kubernetes_secret.tls_cert_private
```

### Applying a plan using a comment

This workflow applies a plan on demand, triggered by someone
commenting `terraform apply` on the PR. The plan is taken
from an existing comment generated by the [`dflook/terraform-plan`](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan)
action.

```yaml
name: Terraform Apply

on: [issue_comment]

jobs:
  apply:
    if: ${{ github.event.issue.pull_request && contains(github.event.comment.body, 'terraform apply') }}
    runs-on: ubuntu-latest
    name: Apply Terraform plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          ref: refs/pull/${{ github.event.issue.number }}/merge

      - name: Terraform apply
        uses: dflook/terraform-apply@v1
        with:
          path: my-terraform-config
```

This example retries the terraform apply operation if it fails.

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
    name: Apply Terraform plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: terraform apply
        uses: dflook/terraform-apply@v1
        continue-on-error: true
        id: first_try
        with:
          path: terraform

      - name: Retry failed apply
        uses: dflook/terraform-apply@v1
        if: ${{ steps.first_try.outputs.failure-reason == 'apply-failed' }}
        with:
          path: terraform
          auto_approve: true
```
