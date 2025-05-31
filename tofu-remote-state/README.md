# tofu-remote-state action

This is one of a suite of OpenTofu related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

Retrieves the root-level outputs from an OpenTofu remote state.

## Inputs

* `backend_type`

  The name of the OpenTofu plugin used for backend state

  - Type: string
  - Required

* `workspace`

  OpenTofu workspace to get the outputs for

  - Type: string
  - Optional
  - Default: `default`

* `backend_config`

  List of OpenTofu backend config values, one per line.

  ```yaml
  with:
    backend_config: token=${{ secrets.BACKEND_TOKEN }}
  ```

  - Type: string
  - Optional

* `backend_config_file`

  List of OpenTofu backend config files to use, one per line.
  Paths should be relative to the GitHub Actions workspace

  ```yaml
  with:
    backend_config_file: prod.backend.tfvars
  ```

  - Type: string
  - Optional

## Outputs

* OpenTofu Outputs

  An action output will be created for each output of the OpenTofu configuration.

  For example, with the OpenTofu config:

  ```hcl
  output "service_hostname" {
    value = "example.com"
  }
  ```

  Running this action will produce a `service_hostname` output with the value `example.com`.

  ### Primitive types (string, number, bool)

  The values for these types get cast to a string with boolean values being 'true' and 'false'.

  ### Complex types (list/set/tuple & map/object)

  The values for complex types are output as a JSON string. OpenTofu `list`, `set` & `tuple` types are cast to a JSON array, `map` and `object` types are cast to a JSON object.

  These values can be used in a workflow expression by using the [fromJSON](https://docs.github.com/en/actions/reference/context-and-expression-syntax-for-github-actions#fromjson) function

## Environment Variables

* `GITHUB_DOT_COM_TOKEN`

  This is used to specify a token for GitHub.com when the action is running on a GitHub Enterprise instance.
  This is only used for downloading OpenTofu binaries from GitHub.com.
  If this is not set, an unauthenticated request will be made to GitHub.com to download the binary, which may be rate limited.

  - Type: string
  - Optional

* `TERRAFORM_CLOUD_TOKENS`

  API token for cloud hosts, of the form `<host>=<token>`. This will be used if the backed type is `remote`.

  e.g:

  ```yaml
  env:
    TERRAFORM_CLOUD_TOKENS: app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
  ```

  With other registries:

  ```yaml
  env:
    TERRAFORM_CLOUD_TOKENS: |
      app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
      tofu.example.com=${{ secrets.TF_REGISTRY_TOKEN }}
  ```

  - Type: string
  - Optional

## Example usage

This example sends a request to a url that has previously been provisioned by OpenTofu, by fetching the url from the remote state in S3.

```yaml
name: Send request

on:
  push:
    branches:
      - main

env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

jobs:
  get_remote_state:
    runs-on: ubuntu-latest
    name: Run Test
    steps:
      - name: Get remote state
        uses: dflook/tofu-remote-state@v2
        id: remote-state
        with:
          backend_type: s3
          backend_config: |
            bucket=tofu-github-actions
            key=tofu-remote-state
            region=eu-west-2

      - name: Send request
        run: |
          curl "${{ steps.remote-state.outputs.url }}"
```
