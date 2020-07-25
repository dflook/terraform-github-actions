# terraform-apply action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action applies a terraform plan.
The default behaviour is to apply the plan that has been added to a PR using the `terraform-plan` action.

If the plan is not found or has changed, then the `apply` action will fail.
This is to ensure that the action only applies changes that have been reviewed by a human.

You can instead set `auto_approve: true` which will generate a plan and apply it immediately, without looking for a plan attached to a PR.

## Demo
This a demo of the process for apply a terraform change using the [`dflook/terraform-plan`](https://github.com/dflook/terraform-github-actions/tree/master/terraform-plan) and [`dflook/terraform-apply`](https://github.com/dflook/terraform-github-actions/tree/master/terraform-apply) actions.

<p align="center">
    <img src="planapply.gif" width="1000">
</p>

## GitHub

To make best use of this action, require that the plan is always reviewed
before merging the PR to approve. You can enforce this in github by
going to the branch settings for the repo and enable protection for
the master branch:

1. Enable 'Require pull request reviews before merging'
2. Check 'Dismiss stale pull request approvals when new commits are pushed'
3. Enable 'Require status checks to pass before merging', and select the job that runs the plan.
4. Enable 'Require branches to be up to date before merging'

## Inputs

* `path`

  Path to the terraform configuration to apply

  - Type: string
  - Required

* `workspace`

  Terraform workspace to run the apply in

  - Type: string
  - Optional
  - Default: `default`

* `label`

  An friendly name for the environment the terraform configuration is for.
  This will be used in the PR comment for easy identification.

  It must be the same as the `label` used in the corresponding `terraform-plan` command.

  - Type: string
  - Optional

* `var`

  Comma separated list of terraform vars to set

  - Type: string
  - Optional

* `var_file`

  Comma separated list of tfvars files to use.
  Paths should be relative to the GitHub Actions workspace

  - Type: string
  - Optional

* `backend_config`

  Comma separated list of terraform backend config values.

  - Type: string
  - Optional

* `backend_config_file`

  Comma separated list of terraform backend config files to use.
  Paths should be relative to the GitHub Actions workspace

  - Type: string
  - Optional

* `parallelism`

  Limit the number of concurrent operations

  - Type: number
  - Optional
  - Default: 10

* `target`

  Comma separated list of targets to apply against, e.g. kubernetes_secret.tls_cert_public,kubernetes_secret.tls_cert_private

  This only takes effect if auto_approve is also set to `true`.

  - Type: string
  - Optional

* `auto_approve`

  When set to `true`, generated plans are always applied.

  The default is `false`, which requires plans to have been approved through a pull request.

  - Type: bool
  - Optional
  - Default: false

## Environment Variables

### `GITHUB_TOKEN`

The GitHub authorization token to use to fetch an approved plan from a PR.
The token provided by GitHub Actions can be used - it can be passed by
using the `${{ secrets.GITHUB_TOKEN }}` expression, e.g.

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Outputs

An action output will be created for each output of the terraform configuration.

For example, with the terraform config:
```hcl
output "service_hostname" {
  value = "example.com"
}
```

Running this action will produce a `service_hostname` output with the same value.
See [terraform-output](https://github.com/dflook/terraform-github-actions/tree/master/terraform-output) for details.

## Example usage

### Apply PR approved plans

This example workflow runs for every push to master. If the commit
came from a PR that has been merged, applies the plan from the PR.

```yaml
name: Apply

on:
  push:
    branches:
      - master

jobs:
  apply:
    runs-on: ubuntu-latest
    name: Apply approved plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: terraform apply
        uses: dflook/terraform-apply@v1
        with:
          path: my-terraform-config
```

### Always apply changes

This example workflow runs for every push to master.
Changes are planned and applied.

```yaml
name: Apply

on:
  push:
    branches:
      - master

jobs:
  apply:
    runs-on: ubuntu-latest
    name: Apply terraform
    steps:
      - name: Checkout
        uses: actions/checkout@v2

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
        uses: actions/checkout@v2

      - name: terraform apply
        uses: dflook/terraform-apply@v1
        with:
          path: my-terraform-config
          auto_approve: true
          target: kubernetes_secret.tls_cert_public,kubernetes_secret.tls_cert_private
```

### Applying a plan using a comment

This workflow applies a plan on demand, triggered by someone
commenting `terraform apply` on the PR. The plan is taken
from an existing comment generated by the [`dflook/terraform-plan`](https://github.com/dflook/terraform-github-actions/tree/master/terraform-plan)
action.

```yaml
name: Terraform Apply

on: [issue_comment]

jobs:
  plan:
    if: github.event.issue.pull_request && contains(github.event.comment.body, 'terraform apply')
    runs-on: ubuntu-latest
    name: Apply terraform plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v2
        with:
          ref: refs/pull/${{ github.event.issue.number }}/merge

      - name: terraform apply
        uses: dflook/terraform-apply@v1
        with:
          path: my-terraform-config
```
