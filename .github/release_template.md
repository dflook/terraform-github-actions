# v0.0.1

All the terraform actions in this repository are released as one.
Use the actions as part of a GitHub Actions workflow, e.g:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - uses: dflook/terraform-plan@v0.0.1
      with:
        path: my-terraform-config
```

You can specify an action version as:
- `@v0.0.1` to use exactly this release
- `@v0.0` to use the latest patch release for the specific minor version
- `@v0` to use the latest minor release for the specific major version

## Changes

### Added
- This is an added feature, which may cause a major version bump

### Changed
- This is a change in behaviour, which may cause a major version bump

### Fixed
- This is backwards compatible bug fix

## Actions
This release includes the actions:
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
