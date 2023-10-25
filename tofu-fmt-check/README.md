# tofu-fmt-check action

This is one of a suite of OpenTofu related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action uses the `tofu fmt` command to check that all files in an OpenTofu configuration directory are in the canonical format.
This can be used to check that files are properly formatted before merging.

If any files are not correctly formatted a failing GitHub check will be added for the file, and the job failed.

## Inputs

* `path`

  Path containing OpenTofu files

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  OpenTofu workspace to inspect when discovering the OpenTofu version to use, if not otherwise specified. 
  See [dflook/tofu-version](https://github.com/dflook/terraform-github-actions/tree/main/tofu-version#tofu-version-action) for details.

  - Type: string
  - Optional

* `backend_config`

  List of OpenTofu backend config values, one per line. This is used for discovering the OpenTofu version to use, if not otherwise specified. 
  See [dflook/tofu-version](https://github.com/dflook/terraform-github-actions/tree/main/tofu-version#tofu-version-action) for details.

  ```yaml
  with:
    backend_config: token=${{ secrets.BACKEND_TOKEN }}
  ```

  - Type: string
  - Optional

* `backend_config_file`

  List of OpenTofu backend config files to use, one per line. This is used for discovering the OpenTofu version to use, if not otherwise specified. 
  See [dflook/tofu-version](https://github.com/dflook/terraform-github-actions/tree/main/tofu-version#tofu-version-action) for details.
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

## Environment Variables

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

This example workflow runs on every push and fails if any of the
OpenTofu files are not formatted correctly.

```yaml
name: Check file formatting

on: [push]

jobs:
  check_format:
    runs-on: ubuntu-latest
    name: Check OpenTofu file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: tofu fmt
        uses: dflook/tofu-fmt-check@v1
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
    name: Check OpenTofu file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: tofu fmt
        uses: dflook/tofu-fmt-check@v1
        id: fmt-check
        with:
          path: my-terraform-config

      - name: Wrong formatting found
        if: ${{ failure() && steps.fmt-check.outputs.failure-reason == 'check-failed' }}
        run: echo "formatting check failed"
```
