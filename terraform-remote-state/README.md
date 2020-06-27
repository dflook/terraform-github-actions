# terraform-remote-state action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

Retrieves the root-level outputs from a terraform remote state.
Only primitive types (string, bool, number) can be retrieved.

## Inputs

* `backend_type`

  The name of the terraform plugin used for backend state

  - Type: string
  - Required

* `workspace`

  Terraform workspace to get the outputs for

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

An output will be created for each root-level output in the terraform remote state.

For example, if the remote state has an output that created using:
```hcl
output "service_hostname" {
  value = "example.com"
}
```
then running this action will produce a "service_hostname" output with the
same value.

## Example usage

This example sends a request to a url that has been provisioned by terraform

```yaml
name: Send request

on:
  push:
    branches:
      master

jobs:
  get_remote_state:
    runs-on: ubuntu-latest
    name: Check terraform file are formatted correctly
    steps:
      - name: Get remote state
        uses: dflook/terraform-remote-state@v1
        id: remote-state
        with:
          backend_type: s3
          backend_config: bucket=terraform-github-actions,key=terraform-remote-state,region=eu-west-2

      - name: Send request
        run: |
          curl "${{ steps.remote-state.outputs.url }}"
```
