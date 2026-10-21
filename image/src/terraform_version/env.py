from __future__ import annotations

import re
import sys
from typing import Iterable, Optional

from github_actions.debug import debug
from github_actions.env import ActionsEnv
from terraform.versions import Version, Constraint, apply_constraints, latest_version


# A version and nothing else. Anything with an operator, a range or a list is a
# constraint, and has to be resolved against the versions that exist.
EXACT_VERSION = re.compile(r'\d+\.\d+\.\d+(?:-[\d\w-]+)?')


def try_read_exact_env(actions_env: ActionsEnv, opentofu: bool = False) -> Optional[Version]:
    """
    Get the version from the environment, if it names one exactly.

    Only the variable belonging to the product being run is considered, so this
    can never pick the other product's version.
    """

    name = 'OPENTOFU_VERSION' if opentofu else 'TERRAFORM_VERSION'

    if name not in actions_env:
        return None

    version = actions_env[name].strip()

    # fullmatch, because Version() would happily read 1.2.3 out of '1.2.3, <2'.
    if not EXACT_VERSION.fullmatch(version):
        return None

    return Version(version, 'OpenTofu' if opentofu else 'Terraform')


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
