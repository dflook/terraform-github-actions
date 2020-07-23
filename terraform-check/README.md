# terraform-check action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

Check for drift in terraform managed resources.
This action runs the terraform plan command, and fails the build if any changes are required.
This is intended to run on a schedule to notify if manual changes to your infrastructure have been made.

## Inputs

* `path`

  Path to the terraform configuration to check

  - Type: string
  - Required

* `workspace`

  Terraform workspace to run the plan in

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

This example workflow runs every morning and will fail if there has been
unexpected changes to your infrastructure.

```yaml
name: Check for infrastructure drift

on:
  schedule:
    - cron:  "0 8 * * *"

jobs:
  check_drift:
    runs-on: ubuntu-latest
    name: Check for drift of terraform configuration
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Check
        uses: dflook/terraform-check@v1
        with:
          path: my-terraform-configuration
```
