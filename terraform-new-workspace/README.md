# terraform-new-workspace action

This is one of a suite of Terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

Creates a new Terraform workspace. If the workspace already exists, succeeds without doing anything.

## Inputs

* `path`

  The path to the Terraform root module directory.

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  The name of the Terraform workspace to create.

  - Type: string
  - Required

* `backend_config`

  List of Terraform backend config values, one per line.

  ```yaml
  with:
    backend_config: token=${{ secrets.BACKEND_TOKEN }}
  ```

  - Type: string
  - Optional

* `backend_config_file`

  List of Terraform backend config files to use, one per line.
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
      terraform.example.com=${{ secrets.TF_REGISTRY_TOKEN }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_SSH_KEY`

  A SSH private key that Terraform will use to fetch git/mercurial module sources.

  This should be in PEM format.

  For example:

  ```yaml
  env:
    TERRAFORM_SSH_KEY: ${{ secrets.TERRAFORM_SSH_KEY }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_HTTP_CREDENTIALS`

  Credentials that will be used for fetching modules sources with `git::http://`, `git::https://`, `http://` & `https://` schemes.

  Credentials have the format `<host>=<username>:<password>`. Multiple credentials may be specified, one per line.

  Each credential is evaluated in order, and the first matching credentials are used.

  Credentials that are used by git (`git::http://`, `git::https://`) allow a path after the hostname.
  Paths are ignored by `http://` & `https://` schemes.
  For git module sources, a credential matches if each mentioned path segment is an exact match.

  For example:

  ```yaml
  env:
    TERRAFORM_HTTP_CREDENTIALS: |
      example.com=dflook:${{ secrets.HTTPS_PASSWORD }}
      github.com/dflook/terraform-github-actions.git=dflook-actions:${{ secrets.ACTIONS_PAT }}
      github.com/dflook=dflook:${{ secrets.DFLOOK_PAT }}
      github.com=graham:${{ secrets.GITHUB_PAT }}  
  ```

  - Type: string
  - Optional

* `TERRAFORM_PRE_RUN`

  A set of commands that will be ran prior to `terraform init`. This can be used to customise the environment before running Terraform.

  The runtime environment for these actions is subject to change in minor version releases. If using this environment variable, specify the minor version of the action to use.

  The runtime image is currently based on `debian:bookworm`, with the command run using `bash -xeo pipefail`.

  For example:

  ```yaml
  env:
    TERRAFORM_PRE_RUN: |
      # Install latest Azure CLI
      curl -skL https://aka.ms/InstallAzureCLIDeb | bash

      # Install postgres client
      apt-get install -y --no-install-recommends postgresql-client
  ```

  - Type: string
  - Optional

## Example usage

This example creates a workspace named after the git branch when the
associated PR is opened or updated, and deploys a test environment to it.

```yaml
name: Run integration tests

on: [pull_request]

jobs:
  integration:
    runs-on: ubuntu-latest
    name: Run integration tests
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Use branch workspace
        uses: dflook/terraform-new-workspace@v2
        with:
          path: terraform
          workspace: ${{ github.head_ref }}

      - name: Deploy test infrastrucutre
        uses: dflook/terraform-apply@v2
        with:
          path: terraform
          workspace: ${{ github.head_ref }}
          auto_approve: true
```
