# terraform-version action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action determines the terraform and provider versions to use for a terraform configuration directory.

The version to use is discovered from the first of:
1. A [`required_version`](https://www.terraform.io/docs/configuration/terraform.html#specifying-a-required-terraform-version)
   constraint in the terraform configuration.
2. A [tfswitch](https://warrensbox.github.io/terraform-switcher/) `.tfswitchrc` file
3. A [tfenv](https://github.com/tfutils/tfenv) `.terraform-version` file in path of the terraform
   configuration.
4. The latest terraform version

The version of terraform and all required providers will be output to the workflow log.

Other terraform actions automatically determine the terraform version
in the same way. You only need to run this action if you want to use the
outputs yourself.

## Inputs

* `path`

  Path to the terraform configuration to apply

  - Type: string
  - Required

## Outputs

* `terraform`

  The terraform version that is used by the terraform configuration

* Provider Versions

  Additional outputs are added with the version of each provider that
  is used by the terraform configuration. For example, if the random
  provider is used:

  ```hcl
  provider "random" {
    version = "2.2.0"
  }
  ```

  A `random` output will be created with the value `2.2.0`.

## Example usage

```yaml
on: [push]

jobs:
  required_version:
    runs-on: ubuntu-latest
    name: Print the required terraform  and provider versions
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Test terraform-version
        uses: dflook/terraform-version@v1
        id: terraform-version
        with:
          path: my-configuration

      - name: Print the version
        run: echo "The terraform version was ${{ steps.terraform-version.outputs.terraform }}"
        
      - name: Print aws provider version
        run: echo "The aws provider version was ${{ steps.terraform-version.outputs.aws }}"        
```
