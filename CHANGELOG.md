# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The actions are versioned as a suite. Some actions may have no change in behaviour between versions.

When using an action you can specify the version as:

- `@v1.1.0` to use an exact release
- `@v1.0` to use the latest patch release for the specific minor version
- `@v1` to use the latest patch release for the specific major version

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

[1.1.0]: https://github.com/olivierlacan/keep-a-changelog/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/dflook/terraform-github-actions/releases/tag/v1.0.0
