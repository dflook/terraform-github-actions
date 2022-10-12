import sys
import os
from pathlib import Path
from typing import Any


def output(name: str, value: Any) -> None:
    if 'GITHUB_OUTPUT' in os.environ and Path(os.environ['GITHUB_OUTPUT']).is_file():
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f'{name}={value}\n')
    else:
        sys.stdout.write(f'::set-output name={name}::{value}\n')

def mask(value: str) -> None:
    sys.stdout.write(f'::add-mask::{value}\n')
