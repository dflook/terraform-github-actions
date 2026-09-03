"""
Parsing for tf json files

These files are not quite structured like HCL files, but they are still valid terraform modules.

We only need limited information from Terraform Modules:
- The required_version constraint
- The backend type
- A list of sensitive variable names
- The backend configuration for remote backends and cloud blocks

This pulls out the relevant information from the tf.json file and returns it in the same format as the HCL parser does.
"""
import json
from pathlib import Path
from typing import Optional, Tuple, Any

from github_actions.debug import debug

def to_list_block(body) -> list:
    """Return the body as a weird HCL-as-JSON list"""
    if isinstance(body, dict):
        return [body]

    if isinstance(body, list):
        return body

    return []

def get_required_version(body: dict) -> Optional[str]:
    """
    Get the required_version constraint string from a tf.json file

    JSON files can be structured as dicts, or in HCL-like list form

    ```json
    {
        "terraform": {
            "required_version": ">= 0.12"
        }
    }
    ```

    ```json
    {
        'terraform': [
            {'required_version': '>= 1.5'}
        ]
    }
    ```
    """

    for terraform_block in to_list_block(body.get('terraform', [])):
        if 'required_version' in terraform_block:
            return terraform_block['required_version']

    return None

def get_backend(body: dict) -> Tuple[Optional[str], dict[str, Any]]:
    """Get the backend type from a tf.json file"""

    for terraform_block in to_list_block(body.get('terraform', {})):

        for cloud_block in to_list_block(terraform_block.get('cloud', [])):

            if 'workspaces' in cloud_block:
                cloud_block['workspaces'] = to_list_block(cloud_block['workspaces'])

            return 'cloud', cloud_block

        for backend_block in to_list_block(terraform_block.get('backend', [])):
            backend_type = next(iter(backend_block.keys()), None)

            actual_backend_config = {}
            for backend_dict in to_list_block(backend_block.get(backend_type, [])):
                actual_backend_config.update(backend_dict)

            if 'workspaces' in actual_backend_config:
                actual_backend_config['workspaces'] = to_list_block(actual_backend_config['workspaces'])
            return backend_type, actual_backend_config

    return None, {}


def get_sensitive_variables(body: dict) -> list[str]:
    """Get the sensitive variable names from a tf file"""

    variables = []

    for variable_block in to_list_block(body.get('variable', [])):
        for variable, config in variable_block.items():
            for config_block in to_list_block(config):
                if config_block.get('sensitive') is True or config_block.get('sensitive') == 'true':
                    variables.append(variable)

    return variables

def load(path: Path) -> dict:
    debug(f'Attempting to parse {path} with json parser')
    with path.open() as f:
        body = json.load(f)

    module: dict[str, list[dict[str, Any]]] = {}

    if constraint := get_required_version(body):
        module['terraform'] = [{
            'required_version': constraint
        }]

    backend_type, backend_config = get_backend(body)
    if backend_type:
        if 'terraform' not in module:
            module['terraform'] = []

        if backend_type == 'cloud':
            module['terraform'].append({'cloud': [backend_config]})
        else:
            module['terraform'].append({'backend': [{backend_type: backend_config}]})

    if sensitive_variables := get_sensitive_variables(body):
        module['variable'] = []
        for variable in sensitive_variables:
            module['variable'].append({
                variable: {
                    'sensitive': True
                }
            })

    return module
