# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The actions are versioned as a suite. Some actions may have no change in behaviour between versions.

When using an action you can specify the version as:

- `@v1.10.0` to use an exact release
- `@v1.10` to use the latest patch release for the specific minor version
- `@v1` to use the latest patch release for the specific major version

## Unreleased

### Added

- The `add_github_comment` input for dflook/terraform-plan may now be set to `changes-only`. This will only add a PR comment
  for plans that result in changes to apply - no comment will be added for plans with no changes.

### Changed

- Improved messaging in the workflow log when dflook/terraform-apply is aborted because the plan has changed
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
