# terraform-fmt action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action uses the `terraform fmt -recursive` command to reformat files in a directory into a canonical format.

## Inputs

* `path`

  Path containing terraform files

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  Terraform workspace to inspect when discovering the terraform version to use, if not otherwise specified. 
  See [dflook/terraform-version](https://github.com/dflook/terraform-github-actions/tree/main/terraform-version#terraform-version-action) for details.

  - Type: string
  - Optional

* `backend_config`

  List of terraform backend config values, one per line. This is used for discovering the terraform version to use, if not otherwise specified. 
  See [dflook/terraform-version](https://github.com/dflook/terraform-github-actions/tree/main/terraform-version#terraform-version-action) for details.

  ```yaml
  with:
    backend_config: token=${{ secrets.BACKEND_TOKEN }}
  ```

  - Type: string
  - Optional

* `backend_config_file`

  List of terraform backend config files to use, one per line. This is used for discovering the terraform version to use, if not otherwise specified. 
  See [dflook/terraform-version](https://github.com/dflook/terraform-github-actions/tree/main/terraform-version#terraform-version-action) for details.
  Paths should be relative to the GitHub Actions workspace

  ```yaml
  with:
    backend_config_file: prod.backend.tfvars
  ```

  - Type: string
  - Optional

## Environment Variables

* `TERRAFORM_CLOUD_TOKENS`

  For the purpose of detecting the terraform version to use from a TFC/E backend.
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

## Example usage

This example automatically creates a pull request to fix any formatting
problems that get merged into the main branch.

```yaml
name: Fix terraform file formatting

on:
  push:
    branches:
      - main

jobs:
  format:
    runs-on: ubuntu-latest
    name: Check terraform file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: terraform fmt
        uses: dflook/terraform-fmt@v1
        with:
          path: my-terraform-config

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: terraform fmt
          title: Reformat terraform files
          body: Update terraform files to canonical format using `terraform fmt`
          branch: automated-terraform-fmt
```
