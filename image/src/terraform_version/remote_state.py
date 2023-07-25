"""Discover the terraform version that wrote an existing state file."""

from __future__ import annotations

import importlib.resources
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable, Optional, Tuple, Union

from github_actions.debug import debug
from github_actions.inputs import InitInputs
from terraform.download import get_executable
from terraform.exec import init_args
from terraform.module import load_backend_config_file, TerraformModule
from terraform.versions import apply_constraints, Constraint, Version, earliest_version, earliest_non_prerelease_version


def read_backend_config_vars(init_inputs: InitInputs) -> dict[str, str]:
    """Read any backend config from input variables."""

    config: dict[str, str] = {}

    for path in init_inputs.get('INPUT_BACKEND_CONFIG_FILE', '').replace(',', '\n').splitlines():
        try:
            config |= load_backend_config_file(Path(path))  # type: ignore
        except Exception as e:
            debug(f'Failed to load backend config file {path}')
            debug(str(e))

    for backend_var in init_inputs.get('INPUT_BACKEND_CONFIG', '').replace(',', '\n').splitlines():
        if match := re.match(r'(.*)\s*=\s*(.*)', backend_var):
            config[match.group(1)] = match.group(2)

    return config


def backend_config(module: TerraformModule) -> Tuple[str, dict[str, Any]]:
    """Return the backend config specified in the terraform module."""

    for terraform in module.get('terraform', []):
        for backend in terraform.get('backend', []):
            for backend_type, config in backend.items():
                return backend_type, config

    return 'local', {}


def get_backend_constraints(module: TerraformModule, backend_config_vars: dict[str, str]) -> list[Constraint]:
    """
    Get any version constraints we can glean from the backend configuration variables

    This should be enough to get a version of terraform that can init the backend and pull the state
    """

    backend_type, config = backend_config(module)
    backend_constraints = json.loads(importlib.resources.read_binary('terraform_version', 'backend_constraints.json'))

    if backend_type not in backend_constraints:
        return []

    constraints = [Constraint(constraint) for constraint in backend_constraints[backend_type]['terraform']]

    for config_var in config | backend_config_vars:
        if config_var not in backend_constraints[backend_type]['config_variables']:
            continue

        for constraint in backend_constraints[backend_type]['config_variables'][config_var]:
            constraints.append(Constraint(constraint))

    for env_var in os.environ:
        if env_var not in backend_constraints[backend_type]['environment_variables']:
            continue

        for constraint in backend_constraints[backend_type]['environment_variables'][env_var]:
            constraints.append(Constraint(constraint))

    return constraints


def dump_backend_hcl(module: TerraformModule) -> str:
    """Return a string representation of the backend config for the given module."""

    def hcl_value(value: str | bool | int | float) -> str:
        """The value as represented in hcl."""
        if isinstance(value, str):
            return f'"{value}"'
        elif value is True:
            return 'true'
        elif value is False:
            return 'false'
        else:
            return str(value)

    backend_type, config = backend_config(module)
    debug(f'{backend_type=}')
    if backend_type == 'local':
        return ''

    tf = 'terraform {\n    backend "' + backend_type + '" {\n'

    for k, v in config.items():
        if isinstance(v, list):
            tf += f'        {k} {{\n'
            for block in v:
                for k, v in block.items():
                    tf += f'            {k} = {hcl_value(v)}\n'
            tf += '        }\n'
        else:
            tf += f'        {k} = {hcl_value(v)}\n'

    tf += '    }\n'
    tf += '}\n'

    return tf


def try_init(terraform: Version, init_args: list[str], workspace: str, backend_tf: str) -> Optional[Union[Version, Constraint]]:
    """
    Try and initialize the specified backend using the specified terraform version.

    Returns the information discovered from doing the init. This could be:
    - Version: the version of terraform used to write the state
    - Constraint: a constraint to apply to the available versions, that further narrows down to the version used to write the state
    - None: There is no remote state
    """

    terraform_path = get_executable(terraform)
    module_dir = tempfile.mkdtemp()

    with open(os.path.join(module_dir, 'terraform.tf'), 'w') as f:
        f.write(backend_tf)

    # Here we go
    result = subprocess.run(
        [str(terraform_path), 'init'] + init_args,
        env=os.environ | {'TF_INPUT': 'false', 'TF_WORKSPACE': workspace},
        capture_output=True,
        cwd=module_dir
    )
    debug(f'{result.args[:2]=}')
    debug(f'{result.returncode=}')
    debug(result.stdout.decode())
    debug(result.stderr.decode())

    if result.returncode != 0:
        if match := re.search(rb'state snapshot was created by Terraform v(.*),', result.stderr):
            return Version(match.group(1).decode())
        elif b'does not support state version 4' in result.stderr:
            return Constraint('>=0.12.0')
        elif b'Failed to select workspace' in result.stderr:
            return None
        else:
            debug(str(result.stderr))
            return None

    result = subprocess.run(
        [terraform_path, 'state', 'pull'],
        env=os.environ | {'TF_INPUT': 'false', 'TF_WORKSPACE': workspace},
        capture_output=True,
        cwd=module_dir
    )
    debug(f'{result.args=}')
    debug(f'{result.returncode=}')
    debug(f'{result.stdout.decode()=}')
    debug(f'{result.stderr.decode()=}')

    if result.returncode != 0:
        if b'does not support state version 4' in result.stderr:
            return Constraint('>=0.12.0')
        raise Exception(result.stderr)

    try:
        state = json.loads(result.stdout.decode())
        if state['version'] == 4 and state['serial'] == 0 and not state.get('outputs', {}):
            return None  # This workspace has no state

        if b'no state' in result.stderr:
            return None

        if terraform < Version('0.12.0'):
            # terraform_version is reported correctly in state output
            return Version(state['terraform_version'])

        # terraform_version is made up
    except Exception as e:
        if b'no state' in result.stderr:
            return None

        debug(str(e))

    # There is some state
    return terraform


def guess_state_version(inputs: InitInputs, module: TerraformModule, versions: Iterable[Version]) -> Optional[Version]:
    """Try and guess the terraform version that wrote the remote state file of the specified module."""

    args = init_args(inputs)
    backend_tf = dump_backend_hcl(module)

    candidate_versions = list(versions)

    while candidate_versions:
        result = try_init(earliest_non_prerelease_version(candidate_versions), args, inputs.get('INPUT_WORKSPACE', 'default'), backend_tf)
        if isinstance(result, Version):
            return result
        elif isinstance(result, Constraint):
            candidate_versions = list(apply_constraints(candidate_versions, [result]))
        elif result is None:
            return None
        else:
            candidate_versions = list(apply_constraints(candidate_versions, [Constraint(f'!={earliest_version(candidate_versions)}')]))

    return None


def try_guess_state_version(inputs: InitInputs, module: TerraformModule, versions: Iterable[Version]) -> Optional[Version]:
    """Try and guess the terraform version that wrote the remote state file of the specified module."""

    try:
        return guess_state_version(inputs, module, versions)
    except Exception as e:
        debug('Failed to find the terraform version from existing state')
        debug(str(e))

    return None
