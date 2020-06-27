# terraform-validate action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action uses the `terraform validate` command to check that a terraform configuration is valid.
This can be used to check that a configuration is valid before creating a plan.

Failing GitHub checks will be added for any problems found.
If the terraform configuration is not valid, the build is failed.

## Inputs

* `path`

  Path to the terraform configuration

  - Type: string
  - Required

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
