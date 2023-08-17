# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The actions are versioned as a suite. Some actions may have no change in behaviour between versions.

When using an action you can specify the version as:

- `@v1.36.2` to use an exact release
- `@v1.36` to use the latest patch release for the specific minor version
- `@v1` to use the latest patch release for the specific major version

## [1.36.2] - 2023-08-17

### Fixed
- When no terraform version is specified and no state file exists the actions will now use the latest terraform version, instead of incorrectly using Terraform 0.9.

## [1.36.1] - 2023-07-15

### Fixed
- The selected workspace was not being shown in the workflow log when using a partial cloud block.

## [1.36.0] - 2023-06-27

### Added
- Support for being triggered by [repository_dispatch](https://docs.github.com/en/actions/reference/events-that-trigger-workflows#repository_dispatch) events.

  Previously [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan) and [dflook/terraform-apply](https://github.com/dflook/terraform-github-actions/tree/main/terraform-apply) couldn't work with PR comments when triggered by repository_dispatch events.
  With this change `repository_dispatch` events that include the PR api url in the client payload will be able to use PR comments.

  The minimum client payload looks like:

  ```json
  {
    "pull_request": {
      "url": "https://api.github.com/repos/dflook/terraform-github-actions/pulls/1"
    }
  }
  ```

## [1.35.0] - 2023-06-18

### Added
- Support for partial or empty cloud blocks. This means you can use a placeholder `cloud` block in your terraform, like so: 

```hcl
terraform {
  cloud {
  }
}
```

  The configuration will be completed with the `TF_CLOUD_ORGANIZATION` and `TF_CLOUD_HOSTNAME` environment variables - the workspace should be specified using the `workspace` input.
  As always, any tokens can be supplied in the `TERRAFORM_CLOUD_TOKENS` environment variable.

## [1.34.0] - 2023-03-10

### Added
- The action image now also builds for `arm64`, meaning these actions will work on linux/arm64 runners.

### Fixed
- Workaround Terraform 1.4.0 sometimes forgetting to output anything.

## [1.33.0] - 2023-02-28

### Added
- The [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan) and [dflook/terraform-apply](https://github.com/dflook/terraform-github-actions/tree/main/terraform-apply) actions now have a `destroy` input.
  When set to `true` terraform will run in destroy mode, planning the destruction of all resources.
  This allows reviewing the effect of a destroy before applying it.

  The [dflook/terraform-destroy](https://github.com/dflook/terraform-github-actions/tree/main/terraform-destroy) action is unchanged and will still immediately destroy all resources.

## [1.32.1] - 2023-02-02

### Fixed
- When triggered by `issue_comment` or `pull_request_review_comment` events, the action will first add a :+1: reaction to the comment

## [1.32.0] - 2023-01-28

### Added
- A new [dflook/terraform-state-unlock](https://github.com/dflook/terraform-github-actions/tree/main/terraform-state-unlock) action. Thanks [patricktalmeida](https://github.com/patricktalmeida) for working on this!
- Actions that fail because the state was locked will now have the `failure-reason` output set to `state-locked`.
  They also have a new `lock-info` output which is a json object with any available lock information.
  This affects [dflook/terraform-apply](https://github.com/dflook/terraform-github-actions/tree/main/terraform-apply), [dflook/terraform-destroy](https://github.com/dflook/terraform-github-actions/tree/main/terraform-destroy), and [dflook/terraform-destroy-worksapce](https://github.com/dflook/terraform-github-actions/tree/main/terraform-destroy-workspace).

### Changed
- If a terraform operation fails because the state is locked the `failure-reason` output will now be set to `state-locked`,
  where before it may have been `apply-failed` or `destroy-failed`. 

## [1.31.1] - 2022-12-01

### Fixed
- Failing to read backend config files for the purpose of identifying the backend state. This meant multiple plans with only
  different backend config files would overwrite each others PR comments.

## [1.31.0] - 2022-11-22

### Added
- Values in the `variables` input of [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan) will be masked in the PR comment if the Terraform variable is marked 'sensitive'. Previously a `label` was required to avoid revealing sensitive values.

## [1.30.0] - 2022-11-19

### Added
- The `TERRAFORM_ACTIONS_GITHUB_TOKEN` environment variable can be set to the github token for the actions to use instead of using `GITHUB_TOKEN`.
  This is useful if using the terraform GitHub provider which also uses the `GITHUB_TOKEN` variable, allowing the github actions and terraform provider to use separate tokens.

- The `GITHUB_TOKEN`/`TERRAFORM_ACTIONS_GITHUB_TOKEN` can now be a github app token or fine grained personal access token. As before, it can also be a classic PAT or use the token provided by github actions.

## [1.29.1] - 2022-10-24

### Fixed
- Multiline string terraform outputs are now properly set as action outputs, and properly masked in the workflow log. 

## [1.29.0] - 2022-10-17

### Added
- Terraform executables are integrity checked using Hashicorp signed checksums before use.

## [1.28.1] - 2022-10-17

### Fixed
- `GITHUB_OUTPUT: unbound variable` errors with v1.28.0 on self-hosted runners with older runner versions.

## [1.28.0] - 2022-10-12

### Added
- Terraform version detection rules updated to include information about backends removed in Terraform 1.3.

### Fixed
- Deprecation warnings about the `set-output` actions workflow command.

## [1.27.0] - 2022-08-07

### Added
- [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan) and [dflook/terraform-apply](https://github.com/dflook/terraform-github-actions/tree/main/terraform-apply) now work with plans that are too large to fit in a PR comment.

  If plan is too large it will be truncated in the comment, with the full plan viewable in the workflow log.
  When [dflook/terraform-apply](https://github.com/dflook/terraform-github-actions/tree/main/terraform-apply) aborts the apply because the plan is outdated, a partial diff will be shown in the workflow log with a link to the full plan for direct comparison.

### Fixed
- Warnings are ignored when deciding if a plan has changed and should no longer cause aborted applies if the order of the warnings changes.
- The unchanged resource attribute count is ignored when deciding if a plan has changed and should no longer cause aborted applies with harmless provider version changes.

## [1.26.0] - 2022-05-29

### Added
- The number of moved resources in a plan is summarised in the PR comment.

### Fixed
- The plan was not being correctly extracted when it contained only resource moves, which resulted in noisy PR comments and may have caused apply operations to be aborted - Thanks to [merykozlowska](https://github.com/merykozlowska)!

## [1.25.1] - 2022-05-10

### Fixed
- Failure to install terraform after change in the download page - Thanks [kylewlacy](https://github.com/kylewlacy)

## [1.25.0] - 2022-05-06

### Added
- New `run_id` output for [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan) and [dflook/terraform-apply](https://github.com/dflook/terraform-github-actions/tree/main/terraform-apply) which are set when using Terraform Cloud/Enterprise. It is the remote run-id of the plan or apply operation.
- The `json_plan_path` output of [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan) now works when using Terraform Cloud/Enterprise.

## [1.24.0] - 2022-05-03

### Added
- New `to_add`, `to_change` and `to_destroy` outputs for the [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan) action that contain the number of resources that would be added, changed or deleted by the plan.

  These can be used in an [if expression](https://docs.github.com/en/enterprise-server@3.2/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idif) in a workflow to conditionally run steps, e.g. when the plan would destroy something. 

## [1.23.0] - 2022-05-02

### Changed
- Input variables no longer help identify the plan comment. Each PR comment is still identified by it's configured terraform backend state file. This is a very subtle change but enables better reporting of why an apply operation is aborted, e.g. "plan has changed" vs "plan not found".

  This means that if you have more than one [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan) action for the same `path` and backend but with different variables, you should ensure they use different `label`s.

- The workflow output when an apply has been aborted because of changes in the plan has been clarified - thanks [toast-gear](https://github.com/toast-gear)!

### Fixed
- Pre-release terraform versions now won't be used when selecting the latest terraform version.
- Invalid terraform files that contained an unterminated string would take an extremely long time to parse before failing the job.
- [dflook/terraform-validate](https://github.com/dflook/terraform-github-actions/tree/main/terraform-validate) now automatically sets `terraform.workspace` to `default` when validating a module that uses a `remote` or `cloud` backend. 

## [1.22.2] - 2022-02-28

### Fixed
- The PR plan comment was incorrectly including resource refresh lines when there were changes to outputs but not resources, while using Terraform >=0.15.4. As well as being noisy, this could lead to failures to apply due to incorrectly detecting changes in the plan.
- Removed incorrect deprecation warning in [dflook/terraform-destroy](https://github.com/dflook/terraform-github-actions/tree/main/terraform-destroy). Thanks [dgrenner](https://github.com/dgrenner)!

## [1.22.1] - 2022-01-24

### Fixed
- Better support for some self-hosted runners that run in containers and don't correctly pass the event payload.

## [1.22.0] - 2022-01-23

### Added
- Workspace management for Terraform Cloud/Enterprise has been reimplemented to avoid issues with the `terraform workspace` command when using the `remote` backend or a cloud config block:
  - [dflook/terraform-new-workspace](https://github.com/dflook/terraform-github-actions/tree/main/terraform-new-workspace) can now create the first workspace
  - [dflook/terraform-destroy-workspace](https://github.com/dflook/terraform-github-actions/tree/main/terraform-destroy-workspace) can now delete the last remaining workspace
  - [dflook/terraform-new-workspace](https://github.com/dflook/terraform-github-actions/tree/main/terraform-new-workspace) and [dflook/terraform-destroy-workspace](https://github.com/dflook/terraform-github-actions/tree/main/terraform-destroy-workspace) work with a `remote` backend that specifies a workspace by `name`
  
- The terraform version to use will now be detected from additional places:

  - The terraform version set in the remote workspace when using Terraform Cloud/Enterprise as the backend 
  - An [asdf](https://asdf-vm.com/) `.tool-versions` file
  - The terraform version that wrote an existing state file
  - A `TERRAFORM_VERSION` environment variable

  The best way to specify the version is using a [`required_version`](https://www.terraform.io/docs/configuration/terraform.html#specifying-a-required-terraform-version) constraint.

  See [dflook/terraform-version](https://github.com/dflook/terraform-github-actions/tree/main/terraform-version#terraform-version-action) docs for details.

### Changed
As a result of the above terraform version detection additions, note these changes:

- Actions always use the terraform version set in the remote workspace when using TFC/E, if it exists. This mostly effects [dflook/terraform-fmt](https://github.com/dflook/terraform-github-actions/tree/main/terraform-fmt), [dflook/terraform-fmt-check](https://github.com/dflook/terraform-github-actions/tree/main/terraform-fmt-check) and [dflook/terraform-validate](https://github.com/dflook/terraform-github-actions/tree/main/terraform-validate).

- If the terraform version is not specified anywhere then new workspaces will be created with the latest terraform version. Existing workspaces will use the terraform version that was last used for that workspace.

- If you want to always use the latest terraform version, instead of not specifying a version you now need to set an open-ended version constraint (e.g. `>1.0.0`)

- All actions now support the inputs and environment variables related to the backend, for discovering the terraform version from a TFC/E workspace or remote state. This add the inputs `workspace`, `backend_config`, `backend_config_file`, and the `TERRAFORM_CLOUD_TOKENS` environment variable to the [dflook/terraform-fmt](https://github.com/dflook/terraform-github-actions/tree/main/terraform-fmt), [dflook/terraform-fmt-check](https://github.com/dflook/terraform-github-actions/tree/main/terraform-fmt-check) and [dflook/terraform-validate](https://github.com/dflook/terraform-github-actions/tree/main/terraform-validate) actions.

- :warning: Some unused packages were removed from the container image, most notably Python 2.

## [1.21.1] - 2021-12-12

### Fixed
- [dflook/terraform-new-workspace](https://github.com/dflook/terraform-github-actions/tree/main/terraform-new-workspace) support for Terraform v1.1.0.

  This stopped working after a change in the behaviour of terraform init.
 
  There is an outstanding [issue in Terraform v1.1.0](https://github.com/hashicorp/terraform/issues/30129) using the `remote` backend that prevents creating a new workspace when no workspaces currently exist.
  If you are affected by this, you can pin to an earlier version of Terraform using one of methods listed in the [dflook/terraform-version](https://github.com/dflook/terraform-github-actions/tree/main/terraform-version#terraform-version-action) docs.

## [1.21.0] - 2021-12-04

### Added
- A new `workspace` input for [dflook/terraform-validate](https://github.com/dflook/terraform-github-actions/tree/main/terraform-validate) 
  allows validating usage of `terraform.workspace` in the terraform code.

  Terraform doesn't initialize `terraform.workspace` based on the backend configuration when running a validate operation.
  This new input allows setting the full name of the workspace to use while validating, even when you wouldn't normally do so for a plan/apply (e.g. when using the `remote` backend)

## [1.20.1] - 2021-12-04

### Fixed
- There was a problem selecting the workspace when using the `remote` backend with a full workspace `name` in the backend block.

## [1.20.0] - 2021-12-03

### Added
- New `text_plan_path` and `json_plan_path` outputs for [dflook/terraform-apply](https://github.com/dflook/terraform-github-actions/tree/main/terraform-apply)
  to match the outputs for [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan).

  These are paths to the generated plan in human-readable and JSON formats.

  If the plan generated by [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan) is different from the plan generated by [dflook/terraform-apply](https://github.com/dflook/terraform-github-actions/tree/main/terraform-apply) the apply step will fail with `failure-reason` set to `plan-changed`.
  These new outputs make it easier to inspect the differences.

## [1.19.0] - 2021-11-01

### Changed
- When triggered by `issue_comment` or `pull_request_review_comment` events, the action will first add a :+1: reaction to the comment
- PR comment status messages include a single emoji that shows progress at a glance
- Actions that don't write to the terraform state no longer lock it.

## [1.18.0] - 2021-10-30

### Added
- A new `replace` input for [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan#inputs) and [dflook/terraform-apply](https://github.com/dflook/terraform-github-actions/tree/main/terraform-apply#inputs)

  This instructs terraform to replace the specified resources, and is available with terraform versions that support replace (v0.15.2 onwards).

  ```yaml
  with:
    replace: |
      random_password.database
  ```

- A `target` input for [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/main/terraform-plan#inputs) to match [dflook/terraform-apply](https://github.com/dflook/terraform-github-actions/tree/main/terraform-apply#inputs)

  `target` limits the plan to the specified resources and their dependencies. This change removes the restriction that `target` can only be used with `auto_approve`.

  ```yaml
  with:
    target: |
      kubernetes_secret.tls_cert_public
      kubernetes_secret.tls_cert_private
  ```

## [1.17.2] - 2021-10-13

### Fixed
- Add `terraform plan` output that was missing from the workflow log

## [1.17.1] - 2021-10-06

### Fixed
- Fix ownership of files created in runner mounted directories

  As the container is run as root, it can cause issues when root owned files are leftover that the runner can't cleanup.
  This would only affect self-hosted, non-ephemeral, non-root runners.

## [1.17.0] - 2021-10-04

### Added
- `variables` and `var_file` support for remote operations in Terraform Cloud/Enterprise.

  The Terraform CLI & Terraform Cloud/Enterprise do not support using variables or variable files with remote plans or applies.
  We can do better. `variables` and `var_file` input variables for the plan, apply & check actions now work, with the expected behavior.

## [1.16.0] - 2021-10-04

### Added
- [dflook/terraform-plan](https://github.com/dflook/terraform-github-actions/tree/master/terraform-plan) has gained two new outputs:
  - `json_plan_path` is a path to the generated plan in a JSON format file
  - `text_plan_path` is a path to the generated plan in a human-readable text file

  These paths are relative to the GitHub Actions workspace and can be read by other steps in the same job.

## [1.15.0] - 2021-09-20

### Added
- Actions that intentionally cause a build failure now set a `failure-reason` output to enable safely responding to those failures.

  Possible failure reasons are:
  - [dflook/terraform-validate](https://github.com/dflook/terraform-github-actions/tree/master/terraform-validate#outputs): validate-failed
  - [dflook/terraform-fmt-check](https://github.com/dflook/terraform-github-actions/tree/master/terraform-fmt-check#outputs): check-failed
  - [dflook/terraform-check](https://github.com/dflook/terraform-github-actions/tree/master/terraform-check#outputs): changes-to-apply
  - [dflook/terraform-apply](https://github.com/dflook/terraform-github-actions/tree/master/terraform-apply#outputs): apply-failed, plan-changed
  - [dflook/terraform-destroy](https://github.com/dflook/terraform-github-actions/tree/master/terraform-destroy#outputs): destroy-failed
  - [dflook/terraform-destroy-workspace](https://github.com/dflook/terraform-github-actions/tree/master/terraform-destroy-workspace#outputs): destroy-failed

### Fixed
- [dflook/terraform-validate](https://github.com/dflook/terraform-github-actions/tree/master/terraform-validate) was sometimes unable to create detailed check failures.

## [1.14.0] - 2021-09-15

### Added
- Support for self-hosted GitHub Enterprise deployments. Thanks [f0rkz](https://github.com/f0rkz)!

### Changed
- The `path` input variable is now optional, defaulting to the Action workspace.
- Uninteresting workflow log output is now grouped and collapsed by default.

### Fixed
- Applying PR approved plans where the plan comment is not within the first 30 comments.

## [1.13.0] - 2021-07-24

### Added
- `TERRAFORM_PRE_RUN` environment variable for customising the environment before running terraform.

  It can be set to a command that will be run prior to `terraform init`.

  The runtime environment for these actions is subject to change in minor version releases.
  If using this environment variable, specify the minor version of the action to use.

  The runtime image is currently based on `debian:buster`, with the command run using `bash -xeo pipefail`.

  For example:
  ```yaml
  env:
    TERRAFORM_PRE_RUN: |
      # Install latest Azure CLI
      curl -skL https://aka.ms/InstallAzureCLIDeb | bash

      # Install postgres client
      apt-get install -y --no-install-recommends postgresql-client
  ```
  
  Thanks to [alec-pinson](https://github.com/alec-pinson) and [GiuseppeChiesa-TomTom](https://github.com/GiuseppeChiesa-TomTom) for working on this feature.

## [1.12.0] - 2021-06-08

### Changed
- [terraform-fmt-check](https://github.com/dflook/terraform-github-actions/tree/master/terraform-fmt-check) now shows a diff in the workflow log when it finds files in non-canonical format

## [1.11.0] - 2021-06-05

### Added
- The `add_github_comment` input for [terraform-plan](https://github.com/dflook/terraform-github-actions/tree/master/terraform-plan) may now be set to `changes-only`. This will only add a PR comment
  for plans that result in changes to apply - no comment will be added for plans with no changes.

### Changed
- Improved messaging in the workflow log when [terraform-apply](https://github.com/dflook/terraform-github-actions/tree/master/terraform-apply) is aborted because the plan has changed
- Update documentation for `backend_config`, `backend_config_file`, `var_file` & `target` inputs to use separate lines for multiple values. 
  Multiple values may still be separated by commas if preferred.

## [1.10.0] - 2021-05-30

### Added
- `TERRAFORM_HTTP_CREDENTIALS` environment variable for configuring the username and password to use for
  `git::https://` & `https://` module sources.

  See action documentation for details, e.g. [terraform-plan](https://github.com/dflook/terraform-github-actions/tree/master/terraform-plan#environment-variables)

## [1.9.3] - 2021-05-29

### Fixed
- With terraform 0.15.4, terraform-plan jobs that only had changes to outputs would fail when creating a PR comment.

## [1.9.2] - 2021-05-05

### Fixed
- Slow state locking messages were being considered part of the plan, which could cause apply actions to be aborted.

## [1.9.1] - 2021-04-21

### Fixed
- Terraform 0.15 plans were not being extracted correctly, causing failures to apply.

## [1.9.0] - 2021-04-10

### Added
- `variables` input for actions that use terraform input variables.

  This value should be valid terraform syntax - like a [variable definition file](https://www.terraform.io/docs/language/values/variables.html#variable-definitions-tfvars-files).
  Variable values set in `variables` override any given in var_files.
  See action documentation for details, e.g. [terraform-plan](https://github.com/dflook/terraform-github-actions/tree/master/terraform-plan#inputs).

### Deprecated
- The `var` input has been deprecated due to the following limitations:
  - Only primitive types can be set with `var` - number, bool and string.
  - String values may not contain a comma.
  - Values set with `var` will be overridden by values contained in `var_file`s

  `variables` is the preferred way to set input variables.

## [1.8.0] - 2021-04-05

### Added
- `TERRAFORM_CLOUD_TOKENS` environment variable for use with Terraform Cloud/Enterprise etc
  when using module registries or a `remote` backend.

- `TERRAFORM_SSH_KEY` environment variable to configure an SSH private key to use for
  [Git Repository](https://www.terraform.io/docs/language/modules/sources.html#generic-git-repository) module sources.

See individual actions for details, e.g. [terraform-validate](https://github.com/dflook/terraform-github-actions/tree/master/terraform-validate#environment-variables).

## [1.7.0] - 2021-04-02

### Added
- Support for the [`pull_request_target`](https://docs.github.com/en/actions/reference/events-that-trigger-workflows#pull_request_target) event
- Support for the [`pull_request_review`](https://docs.github.com/en/actions/reference/events-that-trigger-workflows#pull_request_review) event

### Fixed
- Terraform 0.15 compatibility

## [1.6.0] - 2021-02-25

### Added
- PR comments use a one line summary of the terraform output, with the full output in a collapsable pane.

  If a plan is short the output is shown by default. This can be controlled with the `TF_PLAN_COLLAPSE_LENGTH` environment
  variable for the [dflook/terraform-plan](terraform-plan) action.

### Fixed
- Now makes far fewer github api requests to avoid rate limiting.

## [1.5.2] - 2021-01-16

### Fixed
- Multiple steps in the same job now only download the terraform binary once.

## [1.5.1] - 2020-12-05

### Fixed
- PR comments had an empty plan with Terraform 0.14

## [1.5.0] - 2020-09-18

### Added
- PR comments use HCL highlighting

## [1.4.2] - 2020-09-02

### Fixed
- Using a personal access token instead of the Actions provided token now works.
  This can be used to customise the PR comment author

## [1.4.1] - 2020-08-11

### Fixed
- Latest Terraform versions with a patch version of '0' are correctly detected.
  If not otherwise specified the latest terraform version is used. As of now the latest is v0.13.0.

## [1.4.0] - 2020-07-25

### Added
- Better support for the `issue_comment` and `pull_request_review_comment`
  events in the [dflook/terraform-plan](terraform-plan) and [dflook/terraform-apply](terraform-apply) actions

  This allows using plan PR comments when triggered in reponse to those
  events, enabling workflows like [applying a plan using a comment](terraform-apply#applying-a-plan-using-a-comment).

### Fixed
- Plan errors are now correctly added to the workflow log.

## [1.3.1] - 2020-07-23

### Fixed
- `backend_config_file` and `var_file` now work correctly. Paths should
  be relative to the Action workspace.

## [1.3.0] - 2020-07-22

### Added
- Support for the `remote` backend.

## [1.2.0] - 2020-07-18

### Added
- Complex terraform types are now available as action outputs, which results in a json string approximating the type. See [dflook/terraform-output](terraform-output) for details.
  This also affects the outputs of [dflook/terraform-apply](terraform-apply) and [dflook/terraform-remote-state](terraform-remote-state).

### Fixed
- File path in failing checks is now correct with respect to the repository, and can be clicked through to see the annotation in context.
  This affects the [dflook/terraform-fmt-check](terraform-fmt-check) and [dflook/terraform-validate](terraform-validate) actions.

## [1.1.0] - 2020-07-07

### Added
- The root-level outputs of a terraform configuration are now exposed directly
  by the [dflook/terraform-apply](terraform-apply) action, as if the
  [dflook/terraform-output](terraform-output) action has been run immediately after.

## [1.0.0] - 2020-07-06

First release of the GitHub Actions:
- [dflook/terraform-version](terraform-version)
- [dflook/terraform-remote-state](terraform-remote-state)
- [dflook/terraform-output](terraform-output)
- [dflook/terraform-validate](terraform-validate)
- [dflook/terraform-fmt-check](terraform-fmt-check)
- [dflook/terraform-fmt](terraform-fmt)
- [dflook/terraform-check](terraform-check)
- [dflook/terraform-plan](terraform-plan)
- [dflook/terraform-apply](terraform-apply)
- [dflook/terraform-destroy](terraform-destroy)
- [dflook/terraform-new-workspace](terraform-new-workspace)
- [dflook/terraform-destroy-workspace](terraform-destroy-workspace)

[1.36.2]: https://github.com/dflook/terraform-github-actions/compare/v1.36.1...v1.36.2
[1.36.1]: https://github.com/dflook/terraform-github-actions/compare/v1.36.0...v1.36.1
[1.36.0]: https://github.com/dflook/terraform-github-actions/compare/v1.35.0...v1.36.0
[1.35.0]: https://github.com/dflook/terraform-github-actions/compare/v1.34.0...v1.35.0
[1.34.0]: https://github.com/dflook/terraform-github-actions/compare/v1.33.0...v1.34.0
[1.33.0]: https://github.com/dflook/terraform-github-actions/compare/v1.32.1...v1.33.0
[1.32.1]: https://github.com/dflook/terraform-github-actions/compare/v1.32.0...v1.32.1
[1.32.0]: https://github.com/dflook/terraform-github-actions/compare/v1.31.1...v1.32.0
[1.31.1]: https://github.com/dflook/terraform-github-actions/compare/v1.31.0...v1.31.1
[1.31.0]: https://github.com/dflook/terraform-github-actions/compare/v1.30.0...v1.31.0
[1.30.0]: https://github.com/dflook/terraform-github-actions/compare/v1.29.1...v1.30.0
[1.29.1]: https://github.com/dflook/terraform-github-actions/compare/v1.29.0...v1.29.1
[1.29.0]: https://github.com/dflook/terraform-github-actions/compare/v1.28.1...v1.29.0
[1.28.1]: https://github.com/dflook/terraform-github-actions/compare/v1.28.0...v1.28.1
[1.28.0]: https://github.com/dflook/terraform-github-actions/compare/v1.27.0...v1.28.0
[1.27.0]: https://github.com/dflook/terraform-github-actions/compare/v1.26.0...v1.27.0
[1.26.0]: https://github.com/dflook/terraform-github-actions/compare/v1.25.1...v1.26.0
[1.25.1]: https://github.com/dflook/terraform-github-actions/compare/v1.25.0...v1.25.1
[1.25.0]: https://github.com/dflook/terraform-github-actions/compare/v1.24.0...v1.25.0
[1.24.0]: https://github.com/dflook/terraform-github-actions/compare/v1.23.0...v1.24.0
[1.23.0]: https://github.com/dflook/terraform-github-actions/compare/v1.22.2...v1.23.0
[1.22.2]: https://github.com/dflook/terraform-github-actions/compare/v1.22.1...v1.22.2
[1.22.1]: https://github.com/dflook/terraform-github-actions/compare/v1.22.0...v1.22.1
[1.22.0]: https://github.com/dflook/terraform-github-actions/compare/v1.21.1...v1.22.0
[1.21.1]: https://github.com/dflook/terraform-github-actions/compare/v1.21.0...v1.21.1
[1.21.0]: https://github.com/dflook/terraform-github-actions/compare/v1.20.1...v1.21.0
[1.20.1]: https://github.com/dflook/terraform-github-actions/compare/v1.20.0...v1.20.1
[1.20.0]: https://github.com/dflook/terraform-github-actions/compare/v1.19.0...v1.20.0
[1.19.0]: https://github.com/dflook/terraform-github-actions/compare/v1.18.0...v1.19.0
[1.18.0]: https://github.com/dflook/terraform-github-actions/compare/v1.17.3...v1.18.0
[1.17.3]: https://github.com/dflook/terraform-github-actions/compare/v1.17.2...v1.17.3
[1.17.2]: https://github.com/dflook/terraform-github-actions/compare/v1.17.1...v1.17.2
[1.17.1]: https://github.com/dflook/terraform-github-actions/compare/v1.17.0...v1.17.1
[1.17.0]: https://github.com/dflook/terraform-github-actions/compare/v1.16.0...v1.17.0
[1.16.0]: https://github.com/dflook/terraform-github-actions/compare/v1.15.0...v1.16.0
[1.15.0]: https://github.com/dflook/terraform-github-actions/compare/v1.14.0...v1.15.0
[1.14.0]: https://github.com/dflook/terraform-github-actions/compare/v1.13.0...v1.14.0
[1.13.0]: https://github.com/dflook/terraform-github-actions/compare/v1.12.0...v1.13.0
[1.12.0]: https://github.com/dflook/terraform-github-actions/compare/v1.11.0...v1.12.0
[1.11.0]: https://github.com/dflook/terraform-github-actions/compare/v1.10.0...v1.11.0
[1.10.0]: https://github.com/dflook/terraform-github-actions/compare/v1.9.3...v1.10.0
[1.9.3]: https://github.com/dflook/terraform-github-actions/compare/v1.9.2...v1.9.3
[1.9.2]: https://github.com/dflook/terraform-github-actions/compare/v1.9.1...v1.9.2
[1.9.1]: https://github.com/dflook/terraform-github-actions/compare/v1.9.0...v1.9.1
[1.9.0]: https://github.com/dflook/terraform-github-actions/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/dflook/terraform-github-actions/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/dflook/terraform-github-actions/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/dflook/terraform-github-actions/compare/v1.5.2...v1.6.0
[1.5.2]: https://github.com/dflook/terraform-github-actions/compare/v1.5.1...v1.5.2
[1.5.1]: https://github.com/dflook/terraform-github-actions/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/dflook/terraform-github-actions/compare/v1.4.2...v1.5.0
[1.4.2]: https://github.com/dflook/terraform-github-actions/compare/v1.4.1...v1.4.2
[1.4.1]: https://github.com/dflook/terraform-github-actions/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/dflook/terraform-github-actions/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/dflook/terraform-github-actions/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/dflook/terraform-github-actions/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/dflook/terraform-github-actions/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/dflook/terraform-github-actions/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/dflook/terraform-github-actions/releases/tag/v1.0.0
