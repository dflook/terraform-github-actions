"""Functions for handling terraform modules."""

from __future__ import annotations

import os
from typing import Any, cast, NewType, Optional, TYPE_CHECKING, TypedDict, List

import terraform.hcl

from github_actions.debug import debug
from terraform.versions import Constraint

if TYPE_CHECKING:
    from pathlib import Path

TerraformModule = NewType('TerraformModule', dict[str, list[dict[str, Any]]])


class BackendConfigWorkspaces(TypedDict):
    """A workspaces block from a terraform backend config."""
    name: str
    prefix: str
    tags: list[str]


class BackendConfig(TypedDict):
    """The backend config for a terraform module."""
    hostname: str
    organization: str
    token: str
    workspaces: BackendConfigWorkspaces


def merge(a: TerraformModule, b: TerraformModule) -> TerraformModule:
    """Combine two terraform module objects into one."""

    merged = cast(TerraformModule, {})

    for key in set(a.keys() | b.keys()):
        if isinstance(a.get(key, []), list) and isinstance(b.get(key, []), list):
            if key not in merged:
                merged[key] = []

            merged[key].extend(a.get(key, []))
            merged[key].extend(b.get(key, []))
        else:
            if key in a:
                merged[key] = a[key]
            if key in b:
                merged[key] = b[key]

    return merged


def load_module(path: Path) -> TerraformModule:
    """
    Load the terraform module.

    Every .tf file in the given directory is read and merged into one terraform module.
    If any .tf file fails to parse, it is ignored.
    """

    module = cast(TerraformModule, {})

    for file in os.listdir(path):
        if not file.endswith('.tf'):
            continue

        try:
            tf_file = cast(TerraformModule, terraform.hcl.load(os.path.join(path, file)))
            module = merge(module, tf_file)
        except Exception as e:
            # ignore tf files that don't parse
            debug(f'Failed to parse {file}')
            debug(str(e))

    return module


def load_backend_config_file(path: Path) -> TerraformModule:
    """Load a backend config file."""

    return cast(TerraformModule, terraform.hcl.load(path))


def read_cli_config(config: str) -> dict[str, str]:
    """
    Read a CLI config file

    :param config: The CLI config file contents
    """

    hosts = {}

    config_hcl = terraform.hcl.loads(config)

    for credential in config_hcl.get('credentials', {}):
        for cred_hostname, cred_conf in credential.items():
            if 'token' in cred_conf:
                hosts[cred_hostname] = str(cred_conf['token'])

    return hosts


def get_cli_credentials(path: Path, hostname: str) -> Optional[str]:
    """Get the terraform cloud token for a hostname from a cli credentials file."""

    try:
        with open(os.path.expanduser(path)) as f:
            config = f.read()
    except Exception:
        debug('Failed to parse CLI Config file')
        return None

    credentials = read_cli_config(config)
    return credentials.get(hostname)


def get_version_constraints(module: TerraformModule) -> Optional[list[Constraint]]:
    """Get the Terraform version constraint from the given module."""

    for block in module.get('terraform', []):
        if 'required_version' not in block:
            continue

        try:
            return [Constraint(c) for c in str(block['required_version']).split(',')]
        except Exception:
            debug('required_version constraint is malformed')

    return None


def get_remote_backend_config(
    module: TerraformModule,
    backend_config_files: str,
    backend_config_vars: str,
    cli_config_path: Path
) -> Optional[BackendConfig]:
    """
    A complete backend config

    :param module: The terraform module to get the backend config from. At least a partial backend config must be present.
    :param backend_config_files: Files containing additional backend config.
    :param backend_config_vars: Additional backend config variables.
    :param cli_config_path: A Terraform CLI config file to use.
    """

    found = False
    backend_config = cast(BackendConfig, {
        'hostname': 'app.terraform.io',
        'workspaces': {}
    })

    for terraform in module.get('terraform', []):
        for backend in terraform.get('backend', []):
            if 'remote' not in backend:
                return None

            found = True
            if 'hostname' in backend['remote']:
                backend_config['hostname'] = str(backend['remote']['hostname'])

            backend_config['organization'] = backend['remote'].get('organization')
            backend_config['token'] = backend['remote'].get('token')

            if backend['remote'].get('workspaces', []):
                backend_config['workspaces'] = backend['remote']['workspaces'][0]

    if not found:
        return None

    def read_backend_files() -> None:
        """Read backend config files specified in env var"""
        for file in backend_config_files.replace(',', '\n').splitlines():
            for key, value in load_backend_config_file(Path(file)).items():
                backend_config[key] = value[0] if isinstance(value, list) else value  # type: ignore

    def read_backend_vars() -> None:
        """Read backend config values specified in env var"""
        for line in backend_config_vars.replace(',', '\n').splitlines():
            key, value = line.split('=', maxsplit=1)
            backend_config[key] = value  # type: ignore

    read_backend_files()
    read_backend_vars()

    if backend_config.get('token') is None and cli_config_path:
        if token := get_cli_credentials(cli_config_path, str(backend_config['hostname'])):
            backend_config['token'] = token
        else:
            debug(f'No token found for {backend_config["hostname"]}')
            return backend_config

    return backend_config


def get_cloud_config(module: TerraformModule, cli_config_path: Path) -> Optional[BackendConfig]:
    """
    Get a complete backend config for a module using terraform cloud

    :param module: The terraform module to get the cloud config from.
    :param cli_config_path: A Terraform CLI config file to use.
    """

    found = False
    backend_config = cast(BackendConfig, {
        'hostname': 'app.terraform.io',
        'workspaces': {}
    })

    for terraform in module.get('terraform', []):
        for cloud in terraform.get('cloud', []):

            found = True

            if 'hostname' in cloud:
                backend_config['hostname'] = cloud['hostname']
            elif 'TF_CLOUD_HOSTNAME' in os.environ:
                backend_config['hostname'] = os.environ['TF_CLOUD_HOSTNAME']

            backend_config['organization'] = cloud.get('organization', os.environ.get('TF_CLOUD_ORGANIZATION'))
            backend_config['token'] = cloud.get('token')

            if 'workspaces' in cloud:
                backend_config['workspaces'] = cloud['workspaces'][0]
            elif 'INPUT_WORKSPACE' in os.environ:
                backend_config['workspaces'] = BackendConfigWorkspaces(name=os.environ['INPUT_WORKSPACE'])

    if not found:
        return None

    if backend_config.get('token') is None and cli_config_path:
        if token := get_cli_credentials(cli_config_path, backend_config['hostname']):
            backend_config['token'] = token

    return backend_config


def get_backend_type(module: TerraformModule) -> Optional[str]:
    """
    Get the backend type used by the module.

    :param module: The terraform module to get the backend for
    :return: The name of the backend used by the module
    """

    for terraform in module.get('terraform', []):
        for backend in terraform.get('backend', []):
            for backend_type in backend:
                return str(backend_type)

    for terraform in module.get('terraform', []):
        if 'cloud' in terraform:
            return 'cloud'

    return 'local'

def get_sensitive_variables(module: TerraformModule) -> List[str]:
    sensitive_variables = []

    for variable in module.get('variable', []):
        for variable_name, attributes in variable.items():
            if attributes.get('sensitive', False):
                sensitive_variables.append(variable_name)

    return sensitive_variables
