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

  Comma separated list of terraform backend config files.

  - Type: string
  - Optional

## Example usage

This example creates a workspace named after the git branch when the
associated PR is opened or updated, and deploys a test environment to it.

```yaml
name: Run integration tests

on:
  pull_request

jobs:
  check_format:
    runs-on: ubuntu-latest
    name: Check terraform file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: terraform new-workspace
        uses: dflook/terraform-new-workspace@v1
        with:
          path: my-terraform-config
          workspace: ${{ github.head_ref }}
          
      - name: terraform apply
        uses: dflook/terraform-apply@v1
        with:
          path: my-terraform-config
          workspace: ${{ github.head_ref }}
          auto_approve: true
```
