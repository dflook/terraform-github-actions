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
                # Copy so callers can overlay additional config without affecting the parsed module
                return backend_type, dict(config)

        for cloud in terraform.get('cloud', []):
            return 'cloud', dict(cloud)

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
        if match := re.match(r'(.*?)\s*=\s*(.*)', backend_var):
            config[match.group(1)] = match.group(2)

    return config

# The first version that includes backend config files in the fingerprint. This version also
# started stamping comments with a version header, so comments without one are from earlier
# versions. Versions 1.32.0-1.32.1 stamped comments with '1.31.1', which is fine for this purpose.
COMPLETE_FINGERPRINT_SINCE_VERSION = '1.31.1'

# The first version that overlays the fingerprint with values from the initialised backend,
# read from the terraform data dir. Versions before this fingerprinted only the configured values.
INITIALISED_FINGERPRINT_SINCE_VERSION = '1.49.0'

# The first version that parses the backend_config input by splitting key=value pairs on the
# first '=' instead of the last. Comments created by this version or later never carry legacy
# fingerprints, so are never matched against them.
# This must be no later than the first release that includes the fix.
FIXED_FINGERPRINT_SINCE_VERSION = '2.2.4'

def read_legacy_backend_config_input(init_inputs: InitInputs) -> BackendConfig:
    """
    Read any backend config from input variables, as parsed by old versions.

    Old versions split key=value pairs on the last '=' instead of the first,
    and kept whitespace around the key.
    This is only used to match PR comments created using these old versions,
    until enough time has passed that we don't need to use old comments.
    """

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
    and so created incorrect fingerprints. Comments created by those versions are matched using
    legacy_partial_config, which also parses the backend_config input as they did.
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


def legacy_partial_config(action_inputs: InitInputs, module: TerraformModule) -> Tuple[BackendType, BackendConfig]:
    """
    A partial backend config for the terraform module, as created by old versions.

    This is partial_config with the backend_config input parsed as old versions did.
    This is still used to match PR comments created by versions before
    COMPLETE_FINGERPRINT_SINCE_VERSION, which also didn't stamp comments with a version header.
    """

    backend_type, config = read_module_backend_config(module)

    for key, value in read_legacy_backend_config_input(action_inputs).items():
        config[key] = value

    return backend_type, config


def legacy_complete_config(action_inputs: InitInputs, module: TerraformModule) -> Tuple[BackendType, BackendConfig]:
    """
    The complete backend config for the terraform module, as created by old versions.

    This is complete_config with the backend_config input parsed as old versions did.
    This is still used to match PR comments created by versions from
    COMPLETE_FINGERPRINT_SINCE_VERSION until FIXED_FINGERPRINT_SINCE_VERSION.
    """

    backend_type, config = read_module_backend_config(module)

    for key, value in read_backend_config_files(action_inputs).items():
        config[key] = value

    for key, value in read_legacy_backend_config_input(action_inputs).items():
        config[key] = value

    return backend_type, config
