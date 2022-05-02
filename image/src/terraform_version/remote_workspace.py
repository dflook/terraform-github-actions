from pathlib import Path
from typing import Iterable, Optional

from github_actions.debug import debug
from github_actions.inputs import InitInputs
from terraform.cloud import get_workspace
from terraform.module import TerraformModule, get_remote_backend_config, get_cloud_config
from terraform.versions import Version, latest_non_prerelease_version


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
        version = str(workspace_info['attributes']['terraform-version'])
        if version == 'latest':
            return latest_non_prerelease_version(versions)
        else:
            return Version(version)

    return None


def try_get_remote_workspace_version(inputs: InitInputs, module: TerraformModule, cli_config_path: Path, versions: Iterable[Version]) -> Optional[Version]:
    try:
        return get_remote_workspace_version(inputs, module, cli_config_path, versions)
    except Exception as exception:
        debug('Failed to get terraform version from remote workspace')
        debug(str(exception))

    return None
