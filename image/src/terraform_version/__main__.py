"""Determine the version of terraform to use."""

from __future__ import annotations

import os
import os.path
import sys
from pathlib import Path
from typing import Optional, Iterable, cast

from github_actions.env import ActionsEnv, GithubEnv
from github_actions.inputs import InitInputs
from terraform.cloud import get_workspace
from terraform.download import get_executable
from terraform.module import get_version_constraints, load_module, TerraformModule, get_remote_backend_config, get_cloud_config, get_backend_type
from terraform.versions import apply_constraints, Constraint, get_terraform_versions, latest_version, Version
from terraform_version.asdf import try_read_asdf
from terraform_version.state import get_backend_constraints, read_backend_config_vars, read_local_state, try_guess_state_version
from terraform_version.tfenv import try_read_tfenv
from terraform_version.tfswitch import try_read_tfswitch


def get_remote_workspace_version(inputs: InitInputs, module: TerraformModule, cli_config_path: Path, versions: Iterable[Version]) -> Optional[Version]:
    """Get the terraform version set in a terraform cloud/enterprise workspace."""

    backend_config = get_remote_backend_config(
        module,
        backend_config_files=inputs.get('INPUT_BACKEND_CONFIG_FILE', ''),
        backend_config_vars=inputs.get('INPUT_BACKEND_CONFIG', ''),
        cli_config_path=cli_config_path
    )

    if backend_config is None:
        backend_config = get_cloud_config(
            module,
            cli_config_path=cli_config_path
        )

    if backend_config is None:
        return None

    if workspace_info := get_workspace(backend_config, inputs['INPUT_WORKSPACE']):
        version = str(workspace_info['attributes']['terraform-version'])  # type: ignore
        if version == 'latest':
            return latest_version(versions)
        else:
            return Version(version)

    return None


def determine_version(inputs: InitInputs, cli_config_path: Path, actions_env: ActionsEnv, github_env: GithubEnv) -> Version:
    """Determine the terraform version to use"""

    versions = list(get_terraform_versions())

    if 'INPUT_PATH' not in inputs:
        sys.stdout.write('Using latest terraform version\n')
        return latest_version(versions)

    module = load_module(Path(inputs['INPUT_PATH']))

    version: Optional[Version]

    if version := get_remote_workspace_version(inputs, module, cli_config_path, versions):
        sys.stdout.write(f'Using remote workspace terraform version, which is set to {version!r}\n')
        return version

    if constraints := get_version_constraints(module):
        sys.stdout.write(f'Using latest terraform version that matches the required_version constraints of {constraints!r}\n')
        valid_versions = list(apply_constraints(versions, constraints))
        if not valid_versions:
            raise RuntimeError(f'No versions of terraform match the required_version constraints {constraints}\n')
        return latest_version(valid_versions)

    if version := try_read_tfswitch(inputs):
        sys.stdout.write('Using terraform version specified in .tfswitchrc file\n')
        return version

    if version := try_read_tfenv(inputs, versions):
        sys.stdout.write('Using terraform version specified in .terraform-version file\n')
        return version

    if version := try_read_asdf(inputs, github_env.get('GITHUB_WORKSPACE', '/'), versions):
        sys.stdout.write('Using terraform version specified in .tool-versions file\n')
        return version

    if constraint := actions_env.get('TERRAFORM_VERSION'):
        sys.stdout.write(f'Using latest terraform version that matches the TERRAFORM_VERSION constraints of {constraint!r}\n')
        valid_versions = list(apply_constraints(versions, [Constraint(c) for c in constraint.split(',')]))
        if not valid_versions:
            raise RuntimeError(f'No versions of terraform match TERRAFORM_VERSION constraints {constraint}\n')
        return latest_version(valid_versions)

    backend_config = read_backend_config_vars(inputs)
    versions = list(apply_constraints(versions, get_backend_constraints(module, backend_config)))
    backend_type = get_backend_type(module)

    if backend_type not in ['remote', 'local']:
        if version := try_guess_state_version(inputs, module, versions):
            sys.stdout.write('Using the same terraform version that wrote the existing remote state file\n')
            return version

    if backend_type == 'local':
        if version := read_local_state(Path(inputs['INPUT_PATH'])):
            sys.stdout.write('Using the same terraform version that wrote the existing local terraform.tfstate\n')
            return version

    sys.stdout.write('Terraform version not specified, using the latest version\n')
    return latest_version(versions)


def switch(version: Version) -> None:
    """
    Switch to the specified version of terraform.

    Updates the /usr/local/bin/terraform symlink to point to the specified version.
    The version will be downloaded if it doesn't already exist.
    """

    sys.stdout.write(f'Switching to Terraform v{version}\n')

    target_path = get_executable(version)

    link_path = '/usr/local/bin/terraform'
    if os.path.exists(link_path):
        os.remove(link_path)

    os.symlink(target_path, link_path)


def main() -> None:
    """Entrypoint for terraform-version."""

    if len(sys.argv) > 1:
        switch(Version(sys.argv[1]))
    else:
        version = determine_version(
            cast(InitInputs, os.environ),
            Path('~/.terraformrc'),
            cast(ActionsEnv, os.environ),
            cast(GithubEnv, os.environ)
        )

        switch(version)
