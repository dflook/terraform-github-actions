# terraform-new-workspace action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

Creates a new terraform workspace. If the workspace already exists, succeeds without doing anything.

## Inputs

* `path`

  Path to the terraform configuration

  - Type: string
  - Required

* `workspace`

  Terraform workspace to create

  - Type: string
  - Required

* `backend_config`

  Comma separated list of terraform backend config values.

  - Type: string
  - Optional

* `backend_config_file`

  Comma separated list of terraform backend config files to use.
  Paths should be relative to the GitHub Actions workspace

  - Type: string
  - Optional

## Environment Variables

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

## Example usage

This example creates a workspace named after the git branch when the
associated PR is opened or updated, and deploys a test environment to it.

```yaml
name: Run integration tests

on: [pull_request]

jobs:
  integration:
    runs-on: ubuntu-latest
    name: Run integration tests
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Use branch workspace
        uses: dflook/terraform-new-workspace@v1
        with:
          path: terraform
          workspace: ${{ github.head_ref }}

      - name: Deploy test infrastrucutre
        uses: dflook/terraform-apply@v1
        with:
          path: terraform
          workspace: ${{ github.head_ref }}
          auto_approve: true
```
