# terraform-remote-state action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

Retrieves the root-level outputs from a terraform remote state.

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

For example, with a remote state that has an output created using:
```hcl
output "service_hostname" {
  value = "example.com"
}
```
Running this action will produce a `service_hostname` output with the same value.
See [terraform-output](https://github.com/dflook/terraform-github-actions/tree/master/terraform-output) for details.

## Example usage

This example sends a request to a url that has previously been provisioned by terraform, by fetching the url from the remote state in S3.

```yaml
name: Send request

on:
  push:
    branches:
      - master

env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

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
