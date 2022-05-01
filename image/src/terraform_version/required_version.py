from typing import Optional, Iterable

from github_actions.debug import debug
from terraform.module import get_version_constraints, TerraformModule
from terraform.versions import Version, apply_constraints, latest_non_prerelease_version


def get_required_version(module: TerraformModule, versions: Iterable[Version]) -> Optional[Version]:
    constraints = get_version_constraints(module)
    if constraints is None:
        return None

    valid_versions = list(apply_constraints(versions, constraints))
    if not valid_versions:
        raise RuntimeError(f'No versions of terraform match the required_version constraints {constraints}\n')

    return latest_non_prerelease_version(valid_versions)


def try_get_required_version(module: TerraformModule, versions: Iterable[Version]) -> Optional[Version]:
    try:
        return get_required_version(module, versions)
    except Exception as e:
        debug('Failed to get terraform version from required_version constraint')

    return None
