from __future__ import annotations

from typing import Iterable, Optional

from github_actions.debug import debug
from github_actions.env import ActionsEnv
from terraform.versions import Version, Constraint, apply_constraints, latest_non_prerelease_version


def try_read_env(actions_env: ActionsEnv, versions: Iterable[Version]) -> Optional[Version]:
    if 'TERRAFORM_VERSION' not in actions_env:
        return None

    constraint = actions_env['TERRAFORM_VERSION']

    try:
        valid_versions = list(apply_constraints(versions, [Constraint(c) for c in constraint.split(',')]))
        if not valid_versions:
            return None
        return latest_non_prerelease_version(valid_versions)

    except Exception as exception:
        debug(str(exception))

    return None
