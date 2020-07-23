# terraform-destroy action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action uses the `terraform destroy` command to destroy all resources in a terraform workspace.


## Inputs

* `path`

  Path to the terraform configuration

  - Type: string
  - Required

* `workspace`

  Terraform workspace to destroy

  - Type: string
  - Optional
  - Default: `default`

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

## Example usage

This example destroys the resources in a workspace named after the git branch when the associated PR is closed.

```yaml
name: Cleanup

on:
  pull_request:
    types: [closed] 

jobs:
  destroy_workspace:
    runs-on: ubuntu-latest
    name: Destroy terraform workspace
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: terraform destroy
        uses: dflook/terraform-destroy@v1
        with:
          path: my-terraform-config
          workspace: ${{ github.head_ref }}
```
