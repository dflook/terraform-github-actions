from __future__ import annotations

import sys
from typing import Iterable, Optional

from github_actions.debug import debug
from github_actions.env import ActionsEnv
from terraform.versions import Version, Constraint, apply_constraints, latest_version


def try_read_env(actions_env: ActionsEnv, versions: Iterable[Version]) -> Optional[Version]:
    if 'TERRAFORM_VERSION' in actions_env:
        constraint = actions_env['TERRAFORM_VERSION']
    elif 'OPENTOFU_VERSION' in actions_env:
        constraint = actions_env['OPENTOFU_VERSION']
    else:
        return None

    try:
        valid_versions = list(apply_constraints(versions, [Constraint(c) for c in constraint.split(',')]))
        if not valid_versions:
            sys.stdout.write(f'The constraint {constraint} does not match any available versions\n')
            return None
        return latest_version(valid_versions)

    except Exception as exception:
        debug(str(exception))

    return None
