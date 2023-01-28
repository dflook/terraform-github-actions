# terraform-unlock-state action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This actions is intially planned to manually unlock the state for the defined configuration.

The `GITHUB_TOKEN` environment variable must be set for the PR comment to be added.
The action can be run on other events, which prints the plan to the workflow log.

## Inputs

* `path`

  Path to the terraform root module to apply

  - Type: string
  - Optional
  - Default: The action workspace

* `workspace`

  Terraform workspace to run

  - Type: string
  - Optional
  - Default: `default`

* `lock_id`

  Lock id from the defined configuration

  - Type: string
  - Required

## Environment Variables

* `GITHUB_TOKEN`

  The GitHub authorization token to use to create comments on a PR.
  The token provided by GitHub Actions can be used - it can be passed by
  using the `${{ secrets.GITHUB_TOKEN }}` expression, e.g.

  ```yaml
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```

  The token provided by GitHub Actions will work with the default permissions.
  The minimum permissions are `pull-requests: write`.
  It will also likely need `contents: read` so the job can checkout the repo.

  You can also use any other App token that has `pull-requests: write` permission.

  You can use a fine-grained Personal Access Token which has repository permissions:
  - Read access to metadata
  - Read and Write access to pull requests

  You can also use a classic Personal Access Token which has the `repo` scope.

  The GitHub user or app that owns the token will be the PR comment author.

  - Type: string
  - Optional

* `TERRAFORM_ACTIONS_GITHUB_TOKEN`

  When this is set it is used instead of `GITHUB_TOKEN`, with the same behaviour.
  The GitHub terraform provider also uses the `GITHUB_TOKEN` environment variable, 
  so this can be used to make the github actions and the terraform provider use different tokens.

  - Type: string
  - Optional

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

  A SSH private key that terraform will use to fetch git/mercurial module sources.

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

* `TF_PLAN_COLLAPSE_LENGTH`

  When PR comments are enabled, the terraform output is included in a collapsable pane.
  
  If a terraform plan has fewer lines than this value, the pane is expanded
  by default when the comment is displayed.

  ```yaml
  env:
    TF_PLAN_COLLAPSE_LENGTH: 30
  ```

  - Type: integer
  - Optional
  - Default: 10

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

## Outputs

## Example usage

```yaml
name: "Unlock state"
on:
  workflow_dispatch:
    inputs:
      path:
        description: "Path to the terraform files configuration"
        required: true
      lock_id:
        description: "Lock ID to be unlocked"
        required: true

jobs:
  unlock:
    name: Setup and unlock
    runs-on: ubuntu-latest
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout current branch
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Terraform Unlock
        uses: patricktalmeida/terraform-github-actions/terraform-unlock-state@add-unlock-state
        with:
          path: ${{ github.event.inputs.path }}
          lock_id: ${{ github.event.inputs.lock_id }}

```
