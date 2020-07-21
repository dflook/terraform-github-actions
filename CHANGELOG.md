# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The actions are versioned as a suite. Some actions may have no change in behaviour between versions.

When using an action you can specify the version as:

- `@v1.3.0` to use an exact release
- `@v1.3` to use the latest patch release for the specific minor version
- `@v1` to use the latest patch release for the specific major version

## [1.3.0] - 2020-07-22

### Added
- Support for the `remote` backend

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

[1.3.0]: https://github.com/olivierlacan/keep-a-changelog/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/olivierlacan/keep-a-changelog/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/olivierlacan/keep-a-changelog/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/dflook/terraform-github-actions/releases/tag/v1.0.0
