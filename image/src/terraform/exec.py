"""Functions for executing terraform."""

from __future__ import annotations

import os

from github_actions.inputs import InitInputs


def init_args(inputs: InitInputs) -> list[str]:
    """
    Generate arguments for the `terraform init` command from inputs
    """

    args = []

    for path in inputs.get('INPUT_BACKEND_CONFIG_FILE', '').replace(',', '\n').splitlines():
        if path.strip():
            args.append(f'-backend-config={os.path.relpath(path.strip(), start=inputs["INPUT_PATH"])}')

    for config in inputs.get('INPUT_BACKEND_CONFIG', '').replace(',', '\n').splitlines():
        if stripped := config.strip():
            args.append(f'-backend-config={stripped}')

    return args
