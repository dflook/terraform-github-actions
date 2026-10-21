"""
Deciding the version without resolving anything.

Resolving a constraint means fetching every released version, and asking the
module means parsing every file in it. Neither is needed when the version wanted
is named exactly, and whether that is the case can be worked out from very
little: the blocks that can name a version, and the presence of the files that
can name one.

Only used where it agrees with what the usual resolution would have chosen, so
the order sources are considered in is unchanged.
"""

from __future__ import annotations

import os
import os.path
from pathlib import Path
from typing import Optional

from github_actions.env import ActionsEnv
from github_actions.inputs import InitInputs
from terraform.module import TerraformModule, get_backend_type, get_version_constraints, load_module
from terraform.versions import Version
from terraform_version.env import try_read_exact_env

# The only blocks that can name a version or a backend, so the only files worth
# parsing to find out whether the version is pinned.
VERSION_BLOCKS = ['required_version', 'backend', 'cloud']

# Files that name a version, and so outrank the environment.
VERSION_FILES = ['.tfswitchrc', '.terraform-version', '.opentofu-version']


def exact_required_version(module: TerraformModule, opentofu: bool = False) -> Optional[Version]:
    """
    The version the module requires, if it requires one exactly.

    A single = constraint naming major, minor and patch leaves nothing to
    resolve. Anything else is a constraint and needs the available versions.
    """

    constraints = get_version_constraints(module)

    if constraints is None or len(constraints) != 1:
        return None

    [constraint] = constraints

    if constraint.operator != '=' or constraint.minor is None or constraint.patch is None:
        return None

    version = f'{constraint.major}.{constraint.minor}.{constraint.patch}'
    if constraint.pre_release:
        version += f'-{constraint.pre_release}'

    return Version(version, 'OpenTofu' if opentofu else 'Terraform')


def has_version_file(inputs: InitInputs) -> bool:
    """Whether a file that outranks the environment names a version."""

    module_path = os.path.abspath(inputs.get('INPUT_PATH', '.'))

    if any(os.path.exists(os.path.join(module_path, name)) for name in VERSION_FILES):
        return True

    # .tool-versions is looked for in every parent directory, as try_read_asdf does.
    while module_path != os.path.dirname(module_path):
        if os.path.isfile(os.path.join(module_path, '.tool-versions')):
            return True
        module_path = os.path.dirname(module_path)

    return False


def try_get_exact_version(inputs: InitInputs, actions_env: ActionsEnv, opentofu: bool = False) -> Optional[Version]:
    """Get the version to use, if it can be decided without resolving anything."""

    module = load_module(Path(inputs.get('INPUT_PATH', '.')), declaring=VERSION_BLOCKS)

    # A remote workspace's version outranks everything below it, and reading it
    # needs both the rest of the module and a request to the backend.
    if get_backend_type(module) in ['remote', 'cloud']:
        return None

    if version := exact_required_version(module, opentofu):
        return version

    # Nothing requires a version, so the version files are consulted next and
    # they outrank the environment.
    if has_version_file(inputs):
        return None

    return try_read_exact_env(actions_env, opentofu)
