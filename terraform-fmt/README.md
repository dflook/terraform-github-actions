# terraform-fmt action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action uses the `terraform fmt` command to reformat files in a directory into a canonical format.

## Inputs

* `path`

  Path to the terraform configuration

  - Type: string
  - Required

## Example usage

This example automatically creates a pull request to fix any formatting
problems that get merged into the master branch.

```yaml
name: Fix terraform file formatting

on:
  push:
    branch: master 

jobs:
  format:
    runs-on: ubuntu-latest
    name: Check terraform file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: terraform fmt
        uses: dflook/terraform-fmt@v1
        with:
          path: my-terraform-config
          
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v2
        with:
          commit-message: terraform fmt
          title: Reformat terraform files
          body: Update terraform files to canonical format using `terraform fmt`
          branch: automated-terraform-fmt
```
