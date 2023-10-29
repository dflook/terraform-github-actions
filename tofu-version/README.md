# tofu-version action

This is one of a suite of OpenTofu related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action determines the OpenTofu and provider versions to use for the root module.

The best way to specify the version is using a [`required_version`](https://www.terraform.io/docs/configuration/terraform.html#specifying-a-required-terraform-version) constraint.

The version to use is discovered from the first of:
1. The version set in the cloud workspace if the module uses a `remote` backend or `cloud` configuration, and the remote workspace exists.
2. A [`required_version`](https://www.terraform.io/docs/configuration/terraform.html#specifying-a-required-terraform-version)
   constraint in the OpenTofu configuration. If the constraint is range, the latest matching version is used.
3. A [tfswitch](https://warrensbox.github.io/terraform-switcher/) `.tfswitchrc` file in the module path
4. A [tfenv](https://github.com/tfutils/tfenv) `.terraform-version` file in the module path
5. An [asdf](https://asdf-vm.com/) `.tool-versions` file in the module path or any parent path
6. An `OPENTOFU_VERSION` environment variable containing a [version constraint](https://www.terraform.io/language/expressions/version-constraints). If the constraint allows multiple versions, the latest matching version is used.
7. A `TERRAFORM_VERSION` environment variable containing a [version constraint](https://www.terraform.io/language/expressions/version-constraints). If the constraint allows multiple versions, the latest matching version is used.
8. The OpenTofu version that created the current state file (best effort).
9. The latest OpenTofu version

The version of OpenTofu and all required providers will be output to the workflow log.

Other tofu actions automatically determine the OpenTofu version
in the same way. You only need to run this action if you want to use the
outputs yourself.

## Inputs

* `path`

  Path to the OpenTofu root module

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  The workspace to determine the OpenTofu version for.

  - Type: string
  - Optional
  - Default: `default`

* `backend_config`

  List of OpenTofu backend config values, one per line.

  This will be used to fetch the OpenTofu version set in the cloud workspace if using the `remote` backend.
  For other backend types, this is used to fetch the version that most recently wrote to the OpenTofu state.

  ```yaml
  with:
    backend_config: token=${{ secrets.BACKEND_TOKEN }}
  ```

  - Type: string
  - Optional

* `backend_config_file`

  List of OpenTofu backend config files to use, one per line.
  Paths should be relative to the GitHub Actions workspace

  This will be used to fetch the OpenTofu version set in the cloud workspace if using the `remote` backend.
  For other backend types, this is used to fetch the version that most recently wrote to the OpenTofu state.

  ```yaml
  with:
    backend_config_file: prod.backend.tfvars
  ```

  - Type: string
  - Optional

## Environment Variables

* `TERRAFORM_CLOUD_TOKENS`

  API tokens for cloud hosts, of the form `<host>=<token>`. Multiple tokens may be specified, one per line.
  These tokens may be used for fetching required modules from the registry, and determining the OpenTofu version set in the remote workspace.

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

* `TERRAFORM_SSH_KEY`

  A SSH private key that OpenTofu will use to fetch git module sources.

  This should be in PEM format.

  For example:
  ```yaml
  env:
    TERRAFORM_SSH_KEY: ${{ secrets.TERRAFORM_SSH_KEY }}
  ```

  - Type: string
  - Optional

* `TERRAFORM_PRE_RUN`

  A set of commands that will be ran prior to `tofu init`. This can be used to customise the environment before running OpenTofu. 
  
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

## Outputs

* `terraform`

  The Hashicorp OpenTofu or OpenTofu version that is used by the configuration.

* `tofu`

  If the action chose a version of OpenTofu, this will be set to the version that is used by the configuration.

* Provider Versions

  Additional outputs are added with the version of each provider that
  is used by the OpenTofu configuration. For example, if the random
  provider is used:

  ```hcl
  provider "random" {
    version = "2.2.0"
  }
  ```

  A `random` output will be created with the value `2.2.0`.

## Example usage

```yaml
on: [push]

jobs:
  required_version:
    runs-on: ubuntu-latest
    name: Print the required OpenTofu and provider versions
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Test tofu-version
        uses: dflook/tofu-version@v1
        id: tofu-version
        with:
          path: my-configuration

      - name: Print the version
        run: echo "The version was ${{ steps.terraform-version.outputs.terraform }}"
        
      - name: Print aws provider version
        run: echo "The aws provider version was ${{ steps.terraform-version.outputs.aws }}"        
```
