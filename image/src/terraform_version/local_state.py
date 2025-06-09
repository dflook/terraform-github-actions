import json
import os
from pathlib import Path
from typing import Optional

from github_actions.debug import debug
from terraform.versions import Version


def read_local_state(module_dir: Path) -> Optional[Version]:
    """Return the terraform version that wrote a local terraform.tfstate file."""

    state_path = os.path.join(module_dir, 'terraform.tfstate')

    if not os.path.isfile(state_path):
        return None

    try:
        with open(state_path) as f:
            state = json.load(f)
            if state.get('serial') > 0:
                # Respect OPENTOFU environment variable when determining product type
                # since OpenTofu maintains compatibility with Terraform state files
                product = 'OpenTofu' if 'OPENTOFU' in os.environ else 'Terraform'
                return Version(state.get('terraform_version'), product)
    except Exception as e:
        debug(str(e))

    return None


def try_read_local_state(module_dir: Path) -> Optional[Version]:
    try:
        return read_local_state(module_dir)
    except Exception as e:
        debug(str(e))

    return None
