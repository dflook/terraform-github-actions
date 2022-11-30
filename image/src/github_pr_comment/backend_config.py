import re
import sys
from typing import Tuple, Any
from pathlib import Path
from github_actions.debug import debug
from github_actions.inputs import InitInputs
from terraform.module import TerraformModule, load_backend_config_file

BackendConfig = dict[str, Any]
BackendType = str


def read_module_backend_config(module: TerraformModule) -> Tuple[BackendType, BackendConfig]:
    """Return the backend config specified in the terraform module."""

    for terraform in module.get('terraform', []):
        for backend in terraform.get('backend', []):
            for backend_type, config in backend.items():
                return backend_type, config

        for cloud in terraform.get('cloud', []):
            return 'cloud', cloud

    return 'local', {}


def read_backend_config_files(init_inputs: InitInputs) -> BackendConfig:
    """Read any backend config from backend config files."""

    config: BackendConfig = {}

    for path in init_inputs.get('INPUT_BACKEND_CONFIG_FILE', '').replace(',', '\n').splitlines():
        try:
            config |= load_backend_config_file(Path(path))  # type: ignore
        except Exception as e:
            debug(f'Failed to load backend config file {path}')
            debug(str(e))
            sys.stderr.write(f'Failed to load backend config file {path}\n')
            sys.exit(1)

    return config

def read_backend_config_input(init_inputs: InitInputs) -> BackendConfig:
    """Read any backend config from input variables."""

    config: BackendConfig = {}

    for backend_var in init_inputs.get('INPUT_BACKEND_CONFIG', '').replace(',', '\n').splitlines():
        if match := re.match(r'(.*)\s*=\s*(.*)', backend_var):
            config[match.group(1)] = match.group(2)

    return config

def partial_config(action_inputs: InitInputs, module: TerraformModule) -> Tuple[BackendType, BackendConfig]:
    """
    A partial backend config for the terraform module

    This includes any values from the backend block in the terraform module,
    & any values from the backend_config input.

    This doesn't read from backend config files. Old versions didn't read from backend config files
    and so created incorrect fingerprints. This is still used to match PR comments created using these old
    versions, until enough time has passed that we don't need to use old comments.
    """

    backend_type, config = read_module_backend_config(module)

    for key, value in read_backend_config_input(action_inputs).items():
        config[key] = value

    return backend_type, config


def complete_config(action_inputs: InitInputs, module: TerraformModule) -> Tuple[BackendType, BackendConfig]:
    """
    The complete backend config for the terraform module

    This includes any values from the backend block in the terraform module,
    any values from backend config files & any values from the backend_config input.

    This doesn't include any tfc credentials (not needed for fingerprinting).
    It also doesn't include any config values inferred by the provider.
    """

    backend_type, config = read_module_backend_config(module)

    for key, value in read_backend_config_files(action_inputs).items():
        config[key] = value

    for key, value in read_backend_config_input(action_inputs).items():
        config[key] = value

    return backend_type, config
