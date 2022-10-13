# terraform-check action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

Check for drift in terraform managed resources.
This action runs the terraform plan command, and fails the build if any changes are required.
This is intended to run on a schedule to notify if manual changes to your infrastructure have been made.

## Inputs

* `path`

  Path to the terraform root module to check

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  Terraform workspace to run the plan in

  - Type: string
  - Optional
  - Default: `default`

* `variables`

  Variables to set for the terraform plan. This should be valid terraform syntax - like a [variable definition file](https://www.terraform.io/docs/language/values/variables.html#variable-definitions-tfvars-files).

  ```yaml
  with:
    variables: |
      image_id = "${{ secrets.AMI_ID }}"
      availability_zone_names = [
        "us-east-1a",
        "us-west-1c",
      ]
  ```

  Variables set here override any given in `var_file`s.
  This **can** be used with remote backends such as Terraform Cloud/Enterprise, with variables set in the remote workspace having precedence.

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

  This **can** be used with remote backends such as Terraform Cloud/Enterprise, with variables set in the remote workspace having precedence.

  - Type: string
  - Optional

* `backend_config`

  List of terraform backend config values, one per line.

  ```yaml
  with:
    backend_config: token=${{ secrets.BACKEND_TOKEN }}
  ```

  - Type: string
  - Optional

* `backend_config_file`

  List of terraform backend config files to use, one per line.
  Paths should be relative to the GitHub Actions workspace

  ```yaml
  with:
    backend_config_file: prod.backend.tfvars
  ```

  - Type: string
  - Optional

* `parallelism`

  Limit the number of concurrent operations

  - Type: number
  - Optional
  - Default: The terraform default (10)

* ~~`var`~~

  > :warning: **Deprecated**: Use the `variables` input instead.

  Comma separated list of terraform vars to set

  - Type: string
  - Optional

## Outputs

* `failure-reason`

  When the job outcome is `failure` because the there are outstanding changes to apply, this will be set to 'changes-to-apply'.
  If the job fails for any other reason this will not be set.
  This can be used with the Actions expression syntax to conditionally run a step when there are changes to apply.

## Environment Variables

* `TERRAFORM_CLOUD_TOKENS`

  API tokens for terraform cloud hosts, of the form `<host>=<token>`. Multiple tokens may be specified, one per line.
  These tokens may be used with the `remote` backend and for fetching required modules from the registry.

  e.g for terraform cloud:
  ```yaml
  env:
    TERRAFORM_CLOUD_TOKENS: app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
  ```

  With Terraform Enterprise or other registries:
  ```yaml
  env:
    TERRAFORM_CLOUD_TOKENS: |
      app.terraform.io=${{ secrets.TF_CLOUD_TOKEN }}
      terraform.example.com=${{ secrets.TF_REGISTRY_TOKEN }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_SSH_KEY`

  A SSH private key that terraform will use to fetch git module sources.

  This should be in PEM format.

  For example:
  ```yaml
  env:
    TERRAFORM_SSH_KEY: ${{ secrets.TERRAFORM_SSH_KEY }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_PRE_RUN`

  A set of commands that will be ran prior to `terraform init`. This can be used to customise the environment before running terraform. 
  
  The runtime environment for these actions is subject to change in minor version releases. If using this environment variable, specify the minor version of the action to use.
  
  The runtime image is currently based on `debian:bullseye`, with the command run using `bash -xeo pipefail`.

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

## Example usage

This example workflow runs every morning and will fail if there has been
unexpected changes to your infrastructure.

```yaml
name: Check for infrastructure drift

on:
  schedule:
    - cron:  "0 8 * * *"

jobs:
  check_drift:
    runs-on: ubuntu-latest
    name: Check for drift of terraform configuration
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Check
        uses: dflook/terraform-check@v1
        with:
          path: my-terraform-configuration
```

This example executes a run step only if there are changes to apply.

```yaml
name: Check for infrastructure drift

on:
  schedule:
    - cron:  "0 8 * * *"

jobs:
  check_drift:
    runs-on: ubuntu-latest
    name: Check for drift of terraform configuration
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Check
        uses: dflook/terraform-check@v1
        id: check
        with:
          path: my-terraform-configuration

      - name: Changes detected
        if: ${{ failure() && steps.check.outputs.failure-reason == 'changes-to-apply' }}
        run: echo "There are outstanding terraform changes to apply"
```
