# terraform-output action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

Retrieve the root-level outputs from a terraform configuration.
Only primitive types (string, bool, number) can be retrieved.

## Inputs

* `path`

  Path to the terraform configuration

  - Type: string
  - Required

* `workspace`

  Terraform workspace to get outputs from

  - Type: string
  - Optional
  - Default: `default`

* `backend_config`

  Comma separated list of terraform backend config values.

  - Type: string
  - Optional

* `backend_config_file`

  Comma separated list of terraform backend config files.

  - Type: string
  - Optional

## Outputs

An action output will be created for each output of the terraform configuration.

For example, with the terraform config:
```hcl
output "service_hostname" {
  value = "example.com"
}
```

Running this action will produce a "service_hostname" output with the
same value.

## Example usage

This example prints the terraform `hostname` output.

```yaml
on: [push]

jobs:
  show_hostname:
    runs-on: ubuntu-latest
    name: Show the terraformed hostname
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Get outputs
        uses: dflook/terraform-output@v1
        id: my-terraform-config
        with:
          path: my-terraform-config

      - name: Print the hostname
        run: echo "The terraform version was ${{ steps.my-terraform-config.outputs.hostname }}"
```
