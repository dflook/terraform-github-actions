# terraform-fmt-check action

This is one of a suite of terraform related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).

This action uses the `terraform fmt` command to check that all terraform files in a terraform configuration directory are in the canonical format.
This can be used to check that files are properly formatted before merging.

If any files are not correctly formatted a failing GitHub check will be added for the file, and the job failed.

## Inputs

* `path`

  Path containing terraform files

  - Type: string
  - Optional
  - Default: The action workspace

## Outputs

* `failure-reason`

  When the job outcome is `failure` because the format check failed, this will be set to 'check-failed'.
  If the job fails for any other reason this will not be set.
  This can be used with the Actions expression syntax to conditionally run a step when the format check fails.

## Example usage

This example workflow runs on every push and fails if any of the
terraform files are not formatted correctly.

```yaml
name: Check terraform file formatting

on: [push]

jobs:
  check_format:
    runs-on: ubuntu-latest
    name: Check terraform file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: terraform fmt
        uses: dflook/terraform-fmt-check@v1
        with:
          path: my-terraform-config
```

This example executes a run step only if the format check failed.

```yaml
name: Check terraform file formatting

on: [push]

jobs:
  check_format:
    runs-on: ubuntu-latest
    name: Check terraform file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: terraform fmt
        uses: dflook/terraform-fmt-check@v1
        id: fmt-check
        with:
          path: my-terraform-config

      - name: Wrong formatting found
        if: ${{ failure() && steps.fmt-check.outputs.failure-reason == 'check-failed' }}
        run: echo "terraform formatting check failed"
```
