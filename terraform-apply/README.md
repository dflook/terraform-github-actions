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

These input values must be the same as any `terraform-plan` for the same configuration. (unless auto_approve: true)

* `path`

  Path to the terraform configuration to apply

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  Terraform workspace to run the apply in

  - Type: string
  - Optional
  - Default: `default`

* `label`

  A friendly name for the environment the terraform configuration is for.
  This will be used in the PR comment for easy identification.

  It must be the same as the `label` used in the corresponding `terraform-plan` command.

  - Type: string
  - Optional

* `variables`

  Variables to set for the terraform plan. This should be valid terraform syntax - like a [variable definition file](https://www.terraform.io/docs/language/values/variables.html#variable-definitions-tfvars-files).

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
  This **can** be used with remote backends such as Terraform Cloud/Enterprise, with variables set in the remote workspace having precedence.

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

  This **can** be used with remote backends such as Terraform Cloud/Enterprise, with variables set in the remote workspace having precedence.

  - Type: string
  - Optional

* `backend_config`

  List of terraform backend config values, one per line.

  ```yaml
  with:
    backend_config: token=${{ secrets.BACKEND_TOKEN }}
  ```

  - Type: string
  - Optional

* `backend_config_file`

  List of terraform backend config files to use, one per line.
  Paths should be relative to the GitHub Actions workspace

  ```yaml
  with:
    backend_config_file: prod.backend.tfvars
  ```

  - Type: string
  - Optional

* `parallelism`

  Limit the number of concurrent operations

  - Type: number
  - Optional
  - Default: 10

* `target`

  List of resources to apply, one per line.
  The apply operation will be limited to these resources and their dependencies.
  This only takes effect if auto_approve is also set to `true`.

  ```yaml
  with:
    target: |
      kubernetes_secret.tls_cert_public
      kubernetes_secret.tls_cert_private
  ```

  - Type: string
  - Optional

* `auto_approve`

  When set to `true`, generated plans are always applied.

  The default is `false`, which requires plans to have been approved through a pull request.

  - Type: bool
  - Optional
  - Default: false

* ~~`var`~~

  > :warning: **Deprecated**: Use the `variables` input instead.

  Comma separated list of terraform vars to set.

  This is deprecated due to the following limitations:
  - Only primitive types can be set with `var` - number, bool and string.
  - String values may not contain a comma.
  - Values set with `var` will be overridden by values contained in `var_file`s
  - Does not work with the `remote` backend

  You can change from `var` to `variables` by putting each variable on a separate line and ensuring each string value is quoted.

  For example:
  ```yaml
  with:
    var: instance_type=m5.xlarge,nat_type=instance
  ```
  Becomes:
  ```yaml
  with:
    variables: |
      instance_type="m5.xlarge"
      nat_type="instance"
  ```

  - Type: string
  - Optional

## Outputs

* Terraform Outputs

  An action output will be created for each output of the terraform configuration.

  For example, with the terraform config:
  ```hcl
  output "service_hostname" {
    value = "example.com"
  }
  ```

  Running this action will produce a `service_hostname` output with the same value.
  See [terraform-output](https://github.com/dflook/terraform-github-actions/tree/master/terraform-output) for details.

* `failure-reason`

  When the job outcome is `failure`, this output may be set. The value may be one of:

  - `apply-failed` - The terraform apply operation failed.
  - `plan-changed` - The approved plan is no longer accurate, so the apply will not be attempted.

  If the job fails for any other reason this will not be set.
  This can be used with the Actions expression syntax to conditionally run steps.

## Environment Variables

* `GITHUB_TOKEN`

  The GitHub authorization token to use to fetch an approved plan from a PR.
  The token provided by GitHub Actions can be used - it can be passed by
  using the `${{ secrets.GITHUB_TOKEN }}` expression, e.g.

  ```yaml
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```

  The token provided by GitHub Actions will work with the default permissions.
  The minimum permissions are `pull-requests: write`.
  It will also likely need `contents: read` so the job can checkout the repo.

  You can also use a Personal Access Token which has the `repo` scope.
  This must belong to the same user as the token used by the terraform-plan action

  - Type: string
  - Optional

* `TERRAFORM_CLOUD_TOKENS`

  API tokens for terraform cloud hosts, of the form `<host>=<token>`. Multiple tokens may be specified, one per line.
  These tokens may be used with the `remote` backend and for fetching required modules from the registry.

  e.g for terraform cloud:
  ```yaml
  env:
    TERRAFORM_CLOUD_TOKENS: app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
  ```

  With Terraform Enterprise or other registries:
  ```yaml
  env:
    TERRAFORM_CLOUD_TOKENS: |
      app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
      terraform.example.com=${{ secrets.TF_REGISTRY_TOKEN }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_SSH_KEY`

  A SSH private key that terraform will use to fetch git module sources.

  This should be in PEM format.

  For example:
  ```yaml
  env:
    TERRAFORM_SSH_KEY: ${{ secrets.TERRAFORM_SSH_KEY }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_PRE_RUN`

  A set of commands that will be ran prior to `terraform init`. This can be used to customise the environment before running terraform. 
  
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
          target: |
            kubernetes_secret.tls_cert_public
            kubernetes_secret.tls_cert_private
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
  apply:
    if: ${{ github.event.issue.pull_request && contains(github.event.comment.body, 'terraform apply') }}
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

This example retries the terraform apply operation if it fails.

```yaml
name: Apply plan

on:
  push:
    branches:
      - master

jobs:
  plan:
    runs-on: ubuntu-latest
    name: Apply terraform plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v2

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
