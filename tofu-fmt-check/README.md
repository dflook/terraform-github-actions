# tofu-fmt-check action

This is one of a suite of OpenTofu related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action uses the `tofu fmt` command to check that all files in an OpenTofu configuration directory are in the canonical format.
This can be used to check that files are properly formatted before merging.

If any files are not correctly formatted a failing GitHub check will be added for the file, and the job failed.

## Inputs

* `path`

  The path containing OpenTofu files to check the formatting of.

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  OpenTofu workspace to inspect when discovering the OpenTofu version to use, if the version is not otherwise specified.
  See [dflook/tofu-version](https://github.com/dflook/terraform-github-actions/tree/main/tofu-version#tofu-version-action) for details.

  - Type: string
  - Optional
  - Default: `default`

* `variables`

  Variables to set when initializing OpenTofu. This should be valid OpenTofu syntax - like a [variable definition file](https://opentofu.org/docs/language/values/variables/#variable-definitions-tfvars-files).
  Variables set here override any given in `var_file`s.

  ```yaml
  with:
    variables: |
      image_id = "${{ secrets.AMI_ID }}"
      availability_zone_names = [
        "us-east-1a",
        "us-west-1c",
      ]
  ```

  - Type: string
  - Optional

* `var_file`

  List of tfvars files to use, one per line.
  Paths should be relative to the GitHub Actions workspace

  ```yaml
  with:
    var_file: |
      common.tfvars
      prod.tfvars
  ```

  - Type: string
  - Optional

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
        uses: actions/checkout@v4

      - name: tofu fmt
        uses: dflook/tofu-fmt-check@v2
        with:
          path: my-tofu-config
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
        uses: actions/checkout@v4

      - name: tofu fmt
        uses: dflook/tofu-fmt-check@v2
        id: fmt-check
        with:
          path: my-tofu-config

      - name: Wrong formatting found
        if: ${{ failure() && steps.fmt-check.outputs.failure-reason == 'check-failed' }}
        run: echo "formatting check failed"
```
