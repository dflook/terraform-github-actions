# terraform-fmt-check action

This is one of a suite of Terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action uses the `terraform fmt` command to check that all files in a Terraform configuration directory are in the canonical format.
This can be used to check that files are properly formatted before merging.

If any files are not correctly formatted a failing GitHub check will be added for the file, and the job failed.

## Inputs

* `path`

  The path containing Terraform files to check the formatting of.

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  Terraform workspace to inspect when discovering the Terraform version to use, if the version is not otherwise specified.
  See [dflook/terraform-version](https://github.com/dflook/terraform-github-actions/tree/main/terraform-version#terraform-version-action) for details.

  - Type: string
  - Optional
  - Default: `default`

* `backend_config`

  List of Terraform backend config values, one per line. This is used for discovering the Terraform version to use, if the version is not otherwise specified.
  See [dflook/terraform-version](https://github.com/dflook/terraform-github-actions/tree/main/terraform-version#terraform-version-action) for details.

  ```yaml
  with:
    backend_config: token=${{ secrets.BACKEND_TOKEN }}
  ```

  - Type: string
  - Optional

* `backend_config_file`

  List of Terraform backend config files to use, one per line. This is used for discovering the Terraform version to use, if the version is not otherwise specified.
  See [dflook/terraform-version](https://github.com/dflook/terraform-github-actions/tree/main/terraform-version#terraform-version-action) for details.
  Paths should be relative to the GitHub Actions workspace

  ```yaml
  with:
    backend_config_file: prod.backend.tfvars
  ```

  - Type: string
  - Optional

## Outputs

* `failure-reason`

  When the job outcome is `failure` because the format check failed, this will be set to 'check-failed'.
  If the job fails for any other reason this will not be set.
  This can be used with the Actions expression syntax to conditionally run a step when the format check fails.

  - Type: string

## Environment Variables

* `GITHUB_DOT_COM_TOKEN`

  This is used to specify a token for GitHub.com when the action is running on a GitHub Enterprise instance.
  This is only used for downloading OpenTofu binaries from GitHub.com.
  If this is not set, an unauthenticated request will be made to GitHub.com to download the binary, which may be rate limited.

  - Type: string
  - Optional

* `TERRAFORM_CLOUD_TOKENS`

  For the purpose of detecting the Terraform version to use from a cloud backend.
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

## Example usage

This example workflow runs on every push and fails if any of the
Terraform files are not formatted correctly.

```yaml
name: Check file formatting

on: [push]

jobs:
  check_format:
    runs-on: ubuntu-latest
    name: Check Terraform file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: terraform fmt
        uses: dflook/terraform-fmt-check@v2
        with:
          path: my-terraform-config
```

This example executes a run step only if the format check failed.

```yaml
name: Check file formatting

on: [push]

jobs:
  check_format:
    runs-on: ubuntu-latest
    name: Check Terraform file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: terraform fmt
        uses: dflook/terraform-fmt-check@v2
        id: fmt-check
        with:
          path: my-terraform-config

      - name: Wrong formatting found
        if: ${{ failure() && steps.fmt-check.outputs.failure-reason == 'check-failed' }}
        run: echo "formatting check failed"
```
