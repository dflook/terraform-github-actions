# terraform-refresh action

This is one of a suite of Terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This actions runs a Terraform apply operation in refresh-only mode.
This will synchronise the Terraform state with the actual resources, but will not make any changes to the resources.

## Inputs

* `path`

  Path to the Terraform root module to refresh state for

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  Terraform workspace to run the refresh state in

  - Type: string
  - Optional
  - Default: `default`

* `variables`

  Variables to set for the terraform plan. This should be valid Terraform syntax - like a [variable definition file](https://developer.hashicorp.com/terraform/language/values/variables#variable-definitions-tfvars-files).

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

* `target`

  List of resources to target, one per line.
  The refresh will be limited to these resources and their dependencies.

  ```yaml
  with:
    target: |
      kubernetes_secret.tls_cert_public
      kubernetes_secret.tls_cert_private
  ```

  - Type: string
  - Optional

* `parallelism`

  Limit the number of concurrent operations

  - Type: number
  - Optional
  - Default: The Terraform default (10).

## Outputs

* `failure-reason`

  When the job outcome is `failure`, this output may be set. The value may be one of:

  - `refresh-failed` - The Terraform apply operation failed.
  - `state-locked` - The Terraform state lock could not be obtained because it was already locked.

  If the job fails for any other reason this will not be set.
  This can be used with the Actions expression syntax to conditionally run steps.

  - Type: string

* `lock-info`

  When the job outcome is `failure` and the failure-reason is `state-locked`, this output will be set.

  It is a json object containing any available state lock information and typically has the form:

  ```json
  {
    "ID": "838fbfde-c5cd-297f-84a4-d7578b4a4880",
    "Path": "terraform-github-actions/test-unlock-state",
    "Operation": "OperationTypeApply",
    "Who": "root@e9d43b0c6478",
    "Version": "1.3.7",
    "Created": "2023-01-28 00:16:41.560904373 +0000 UTC",
    "Info": ""
  }
  ```

  - Type: string

* `run_id`

  If the root module uses the `remote` or `cloud` backend in remote execution mode, this output will be set to the remote run id.

  - Type: string

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
