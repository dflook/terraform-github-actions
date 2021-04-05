# terraform-validate action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action uses the `terraform validate` command to check that a terraform configuration is valid.
This can be used to check that a configuration is valid before creating a plan.

Failing GitHub checks will be added for any problems found.

<p align="center">
    <img src="validate.png" width="1000">
</p>

If the terraform configuration is not valid, the build is failed.

## Inputs

* `path`

  Path to the terraform configuration

  - Type: string
  - Required

## Environment Variables

* `TERRAFORM_CLOUD_TOKENS`

  API tokens for terraform cloud hosts, of the form `<host>=<token>`. Multiple tokens may be specified, one per line.
  These tokens may be used for fetching required modules from the registry.

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

This example workflow runs on every push and fails if the terraform
configuration is invalid.

```yaml
on: [push]

jobs:
  validate:
    runs-on: ubuntu-latest
    name: Validate terraform
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: terraform validate
        uses: dflook/terraform-validate@v1
        with:
          path: my-terraform-config
```
