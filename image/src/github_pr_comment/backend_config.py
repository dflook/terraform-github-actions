import re
from typing import Tuple, Any
from pathlib import Path
from github_actions.debug import debug
from github_actions.inputs import InitInputs
from terraform.module import TerraformModule, load_backend_config_file

BackendConfig = dict[str, Any]
BackendType = str


def partial_backend_config(module: TerraformModule) -> Tuple[BackendType, BackendConfig]:
    """Return the backend config specified in the terraform module."""

    for terraform in module.get('terraform', []):
        for backend in terraform.get('backend', []):
            for backend_type, config in backend.items():
                return backend_type, config

        for cloud in terraform.get('cloud', []):
            return 'cloud', cloud

    return 'local', {}


def read_backend_config_vars(init_inputs: InitInputs) -> BackendConfig:
    """Read any backend config from input variables."""

    config: BackendConfig = {}

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


def complete_config(action_inputs: InitInputs, module: TerraformModule) -> Tuple[BackendType, BackendConfig]:
    backend_type, config = partial_backend_config(module)

    for key, value in read_backend_config_vars(action_inputs).items():
        config[key] = value

    return backend_type, config
