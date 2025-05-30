# Terraform and OpenTofu GitHub Actions ![release](https://img.shields.io/github/v/release/dflook/terraform-github-actions)![job runs](https://img.shields.io/docker/pulls/danielflook/terraform-github-actions?label=job%20runs)

This is a suite of Terraform and OpenTofu related GitHub Actions that can be used together to build effective Infrastructure as Code workflows.

[GitHub Actions](https://github.com/features/actions) are a way to make automated workflows that trigger when events occur on your GitHub repository, using a YAML file that lives in your repo.
These actions can be used to easily perform [Terraform](https://www.terraform.io/) or [OpenTofu](https://www.opentofu.org/) tasks as part of your workflow.

## Actions

See the documentation for the available actions:

| Terraform                                                         | OpenTofu                                                |
|-------------------------------------------------------------------|---------------------------------------------------------|
| [dflook/terraform-plan](terraform-plan)                           | [dflook/tofu-plan](tofu-plan)                           |
| [dflook/terraform-apply](terraform-apply)                         | [dflook/tofu-apply](tofu-apply)                         |
| [dflook/terraform-output](terraform-output)                       | [dflook/tofu-output](tofu-output)                       |
| [dflook/terraform-remote-state](terraform-remote-state)           | [dflook/tofu-remote-state](tofu-remote-state)           |
| [dflook/terraform-validate](terraform-validate)                   | [dflook/tofu-validate](tofu-validate)                   |
| [dflook/terraform-fmt-check](terraform-fmt-check)                 | [dflook/tofu-fmt-check](tofu-fmt-check)                 |
| [dflook/terraform-fmt](terraform-fmt)                             | [dflook/tofu-fmt](tofu-fmt)                             |
| [dflook/terraform-check](terraform-check)                         | [dflook/tofu-check](tofu-check)                         |
| [dflook/terraform-new-workspace](terraform-new-workspace)         | [dflook/tofu-new-workspace](tofu-new-workspace)         |
| [dflook/terraform-destroy-workspace](terraform-destroy-workspace) | [dflook/tofu-destroy-workspace](tofu-destroy-workspace) |
| [dflook/terraform-destroy](terraform-destroy)                     | [dflook/tofu-destroy](tofu-destroy)                     |
| [dflook/terraform-version](terraform-version)                     | [dflook/tofu-version](tofu-version)                     |
| [dflook/terraform-unlock-state](terraform-unlock-state)           | [dflook/tofu-unlock-state](tofu-unlock-state)           |
| [dflook/terraform-test](terraform-test)                           | [dflook/tofu-test](tofu-test)                           |
| [dflook/terraform-refresh](terraform-refresh)                     | [dflook/tofu-refresh](tofu-refresh)                     |

## Example Usage

These actions can be added as steps to your own workflow files.
GitHub reads workflow files from `.github/workflows/` within your repository.
See the [Workflow documentation](https://docs.github.com/en/actions/configuring-and-managing-workflows/configuring-a-workflow#about-workflows) for details on writing workflows.

Here are some examples of how the actions can be used together in workflows.

### Terraform plan PR approval

Terraform plans typically need to be reviewed by a human before being applied.
Fortunately, GitHub has a well established method for requiring human reviews of changes - a Pull Request.

We can use PRs to safely plan and apply infrastructure changes.

<p align="center">
    <img src="terraform-apply/planapply.gif" width="960" alt="A video showing a PR being created, a plan being generated, the plan being reviewed, and the plan being applied.">
</p>

You can make GitHub enforce this using branch protection, see the [dflook/terraform-apply](terraform-apply) action for details.

In this example we use two workflows:

#### plan.yaml

This workflow runs on changes to a PR branch. It generates a Terraform plan and attaches it to the PR as a comment.

```yaml
name: Create terraform plan

on: [pull_request]

permissions:
  contents: read
  pull-requests: write

jobs:
  plan:
    runs-on: ubuntu-latest
    name: Create a plan for an example terraform configuration
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: terraform plan
        uses: dflook/terraform-plan@v2
        with:
          path: my-terraform-config
```

#### apply.yaml

This workflow runs when the PR is merged into the main branch, and applies the planned changes.

```yaml
name: Apply terraform plan

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pull-requests: write

jobs:
  apply:
    runs-on: ubuntu-latest
    name: Apply terraform plan
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: terraform apply
        uses: dflook/terraform-apply@v2
        with:
          path: my-terraform-config
```

### Linting

This workflow runs on every push to non-main branches and checks the terraform configuration is valid.
For extra strictness, we check the files are in the canonical format.

<p align="center">
    <img src="terraform-validate/validate.png" width="1000" alt="A screenshot showing the output of the terraform validate action.">
</p>

This can be used to check for correctness before merging.

#### lint.yaml

```yaml
name: Lint

on:
  push:
    branches-ignore:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest
    name: Validate terraform configuration
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: terraform validate
        uses: dflook/terraform-validate@v2
        with:
          path: my-terraform-config

  fmt-check:
    runs-on: ubuntu-latest
    name: Check formatting of terraform files
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: terraform fmt
        uses: dflook/terraform-fmt-check@v2
        with:
          path: my-terraform-config
```

### Checking for drift

This workflow runs every morning and checks that the state of your infrastructure matches the configuration.

This can be used to detect manual or misapplied changes before they become a problem.
If there are any unexpected changes, the workflow will fail.

#### drift.yaml

```yaml
name: Check for infrastructure drift

on:
  schedule:
    - cron:  "0 8 * * *"

jobs:
  check_drift:
    runs-on: ubuntu-latest
    name: Check for drift of example terraform configuration
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Check for drift
        uses: dflook/terraform-check@v2
        with:
          path: my-terraform-config
```

### Scheduled infrastructure updates

There may be times when you expect Terraform to plan updates without any changes to your configuration files.
Your configuration could be consuming secrets from elsewhere, or renewing certificates every few months.

This example workflow runs every morning and applies any outstanding changes to those specific resources.

#### rotate-certs.yaml

```yaml
name: Rotate TLS certificates

on:
  schedule:
    - cron:  "0 8 * * *"

jobs:
  rotate_certs:
    runs-on: ubuntu-latest
    name: Rotate TLS certificates in example terraform configuration
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Rotate certs
        uses: dflook/terraform-apply@v2
        with:
          path: my-terraform-config
          auto_approve: true
          target: |
            acme_certificate.certificate
            kubernetes_secret.certificate
```

### Automatically fixing formatting

Perhaps you don't want to spend engineer time making formatting changes. This workflow will automatically create or update a PR that fixes any formatting issues.

#### fmt.yaml

```yaml
name: Check terraform file formatting

on:
  push:
    branches: 
      - main 

jobs:
  format:
    runs-on: ubuntu-latest
    name: Check terraform file are formatted correctly
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: terraform fmt
        uses: dflook/terraform-fmt@v2
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

### Ephemeral test environments

Testing of software changes often requires some supporting infrastructure, like databases, DNS records, compute environments etc.
We can use these actions to create dedicated resources for each PR which is used to run tests.

There are two workflows:

#### integration-test.yaml

This workflow runs with every change to a PR.

It deploys the testing infrastructure using a Terraform workspace dedicated to this branch, then runs integration tests against the new infrastructure.

```yaml
name: Run integration tests

on: [pull_request]

jobs:
  run_tests:
    runs-on: ubuntu-latest
    name: Run integration tests
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Use branch workspace
        uses: dflook/terraform-new-workspace@v2
        with:
          path: my-terraform-config
          workspace: ${{ github.head_ref }}
          
      - name: Deploy test infrastrucutre
        uses: dflook/terraform-apply@v2
        id: test-infra
        with:
          path: my-terraform-config
          workspace: ${{ github.head_ref }}
          auto_approve: true

      - name: Run tests
        run: |
          ./run-tests.sh --endpoint "${{ steps.test-infra.outputs.url }}"
```

#### integration-test-cleanup.yaml

This workflow runs when a PR is closed and destroys any testing infrastructure that is no longer needed.

```yaml
name: Destroy testing workspace

on:
  pull_request:
    types: [closed] 

jobs:
  cleanup_tests:
    runs-on: ubuntu-latest
    name: Cleanup after integration tests
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: terraform destroy
        uses: dflook/terraform-destroy-workspace@v2
        with:
          path: my-terraform-config
          workspace: ${{ github.head_ref }}
```
