"""Determine the version of terraform to use."""

from __future__ import annotations

import os
import os.path
import sys
from pathlib import Path
from typing import Optional, cast

from github_actions.debug import debug
from github_actions.env import ActionsEnv, GithubEnv
from github_actions.inputs import InitInputs
from terraform.download import get_executable, get_arch, DownloadError
from terraform.module import load_module, get_backend_type
from terraform.versions import apply_constraints, get_terraform_versions, Version, Constraint, latest_non_prerelease_version
from terraform_version.asdf import try_read_asdf
from terraform_version.env import try_read_env
from terraform_version.local_state import try_read_local_state
from terraform_version.remote_state import get_backend_constraints, read_backend_config_vars, try_guess_state_version
from terraform_version.remote_workspace import try_get_remote_workspace_version
from terraform_version.required_version import try_get_required_version
from terraform_version.tfenv import try_read_tfenv
from terraform_version.tfswitch import try_read_tfswitch
from opentofu.download import get_executable as get_opentofu_executable
from opentofu.versions import get_opentofu_versions


def determine_version(inputs: InitInputs, cli_config_path: Path, actions_env: ActionsEnv, github_env: GithubEnv) -> Version:
    """Determine the terraform version to use"""

    versions = list(get_terraform_versions())

    if 'OPENTOFU' in os.environ:
        versions = list(apply_constraints(versions, [Constraint('<1.6.0')]))
        versions.extend(get_opentofu_versions())

    module = load_module(Path(inputs.get('INPUT_PATH', '.')))

    version: Optional[Version]

    if version := try_get_remote_workspace_version(inputs, module, cli_config_path, versions):
        sys.stdout.write(f'Using remote workspace terraform version, which is set to {version!r}\n')
        return version

    if version := try_get_required_version(module, versions):
        sys.stdout.write(f'Using latest {version.product} version that matches the required_version constraints\n')
        return version

    if version := try_read_tfswitch(inputs):
        sys.stdout.write(f'Using {version.product} version specified in .tfswitchrc file\n')
        return version

    if version := try_read_tfenv(inputs, versions):
        sys.stdout.write(f'Using {version.product} version specified in .terraform-version file\n')
        return version

    if version := try_read_asdf(inputs, github_env.get('GITHUB_WORKSPACE', '/'), versions):
        sys.stdout.write(f'Using {version.product} version specified in .tool-versions file\n')
        return version

    if version := try_read_env(actions_env, versions):
        env_var = 'OPENTOFU_VERSION' if 'OPENTOFU_VERSION' in os.environ else 'TERRAFORM_VERSION'
        sys.stdout.write(f'Using latest {version.product} version that matches the {env_var} constraints\n')
        return version

    if inputs.get('INPUT_BACKEND_CONFIG', '').strip():
        # key=value form of backend config was introduced in 0.9.1
        versions = list(apply_constraints(versions, [Constraint('>=0.9.1')]))

    try:
        backend_config = read_backend_config_vars(inputs)
        versions = list(apply_constraints(versions, get_backend_constraints(module, backend_config)))
        backend_type = get_backend_type(module)
    except Exception as e:
        debug('Failed to get backend config')
        debug(str(e))
        return latest_non_prerelease_version(versions)

    if backend_type == 'local':
        if version := try_read_local_state(Path(inputs.get('INPUT_PATH', '.'))):
            sys.stdout.write(f'Using the same {version.product} version that wrote the existing local terraform.tfstate\n')
            return version

    if get_arch() == 'arm64':
        # arm64 support was introduced in 0.13.5
        versions = list(apply_constraints(versions, [Constraint('>=0.13.5')]))

    if backend_type not in ['remote', 'cloud', 'local']:
        if version := try_guess_state_version(inputs, module, versions):
            sys.stdout.write(f'Using the same {version.product} version that wrote the existing remote state file\n')
            return version

    sys.stdout.write(f'Version not specified, using the latest release version\n')
    return latest_non_prerelease_version(versions)


def switch(version: Version) -> None:
    """
    Switch to the specified version of terraform.

    Updates the /usr/local/bin/terraform symlink to point to the specified version.
    The version will be downloaded if it doesn't already exist.
    """

    if version.product == 'OpenTofu':
        target_path = get_opentofu_executable(version)
    else:
        target_path = get_executable(version)

    link_path = '/usr/local/bin/terraform'
    if os.path.exists(link_path):
        os.remove(link_path)

    os.symlink(target_path, link_path)

    if version.product == 'OpenTofu':
        link_path = '/usr/local/bin/tofu'
        if os.path.exists(link_path):
            os.remove(link_path)

        os.symlink(target_path, link_path)

    sys.stdout.write(f'Switched to {version.product} v{version}\n')

def main() -> None:
    """Entrypoint for terraform-version."""

    try:
        if len(sys.argv) > 1:
            switch(Version(sys.argv[1]))

        else:
            version = determine_version(
                cast(InitInputs, os.environ),
                Path('~/.terraformrc'),
                cast(ActionsEnv, os.environ),
                cast(GithubEnv, os.environ)
            )

            if version is None:
                if 'OPENTOFU' in os.environ:
                    sys.stderr.write('No release version of OpenTofu found. Try specifying a pre-release version, e.g. OPENTOFU_VERSION=1.6.0-alpha3\n')
                else:
                    sys.stderr.write('No eligible versions found\n')
                sys.exit(1)

            if 'OPENTOFU' in os.environ and version.product == 'Terraform':
                sys.stdout.write(f'OpenTofu is preferred, but only a version of Terraform matched the version constraints.\n')
                sys.stdout.write(f'Try specifying a version of OpenTofu. Pre-release versions must be explicit, e.g. OPENTOFU_VERSION=1.6.0-alpha3\n')

            switch(version)

    except DownloadError as download_error:
        sys.stderr.write(str(download_error))
        sys.exit(1)
