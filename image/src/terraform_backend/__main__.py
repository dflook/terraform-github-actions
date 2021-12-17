"""
Output the backend type in use by the terraform module in the current path

Usage:
    terraform-backend
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from terraform.module import load_module, get_backend_type


def main() -> None:
    """Entrypoint for terraform-backend"""

    module = load_module(Path(os.environ.get('INPUT_PATH', '.')))
    sys.stdout.write(f'{get_backend_type(module)}\n')
