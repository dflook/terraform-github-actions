# tofu-fmt action

This is one of a suite of OpenTofu related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action uses the `tofu fmt -recursive` command to reformat files in a directory into a canonical format.

## Inputs

* `path`

  The path containing OpenTofu files to format.

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  OpenTofu workspace to inspect when discovering the OpenTofu version to use, if the version is not otherwise specified. 
  See [dflook/tofu-version](https://github.com/dflook/terraform-github-actions/tree/main/tofu-version#tofu-version-action) for details.

  - Type: string
  - Optional
  - Default: `default`

* `backend_config`

  List of OpenTofu backend config values, one per line. This is used for discovering the OpenTofu version to use, if the version is not otherwise specified. 
  See [dflook/tofu-version](https://github.com/dflook/terraform-github-actions/tree/main/tofu-version#tofu-version-action) for details.

  ```yaml
  with:
    backend_config: token=${{ secrets.BACKEND_TOKEN }}
  ```

  - Type: string
  - Optional

* `backend_config_file`

  List of OpenTofu backend config files to use, one per line. This is used for discovering the OpenTofu version to use, if the version is not otherwise specified. 
  See [dflook/tofu-version](https://github.com/dflook/terraform-github-actions/tree/main/tofu-version#tofu-version-action) for details.
  Paths should be relative to the GitHub Actions workspace

  ```yaml
  with:
    backend_config_file: prod.backend.tfvars
  ```

  - Type: string
  - Optional

## Environment Variables

* `GITHUB_DOT_COM_TOKEN`

  This is used to specify a token for GitHub.com when the action is running on a GitHub Enterprise instance.
  This is only used for downloading OpenTofu binaries from GitHub.com.
  If this is not set, an unauthenticated request will be made to GitHub.com to download the binary, which may be rate limited.

  - Type: string
  - Optional

* `TERRAFORM_CLOUD_TOKENS`

  For the purpose of detecting the OpenTofu version to use from a cloud backend.
  API tokens for cloud hosts, of the form `<host>=<token>`. Multiple tokens may be specified, one per line.
  These tokens may be used with the `remote` backend and for fetching required modules from the registry.

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

This example automatically creates a pull request to fix any formatting
problems that get merged into the main branch.

```yaml
name: Fix OpenTofu file formatting

on:
  push:
    branches:
      - main

jobs:
  format:
    runs-on: ubuntu-latest
    name: Check OpenTofu file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: tofu fmt
        uses: dflook/tofu-fmt@v1
        with:
          path: my-tofu-config

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: tofu fmt
          title: Reformat tofu files
          body: Update OpenTofu files to canonical format using `tofu fmt`
          branch: automated-tofu-fmt
```
