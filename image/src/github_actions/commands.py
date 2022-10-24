import random
import string
import sys
import os
from pathlib import Path
from typing import Any

def generate_delimiter():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(20))

def output(name: str, value: Any) -> None:
    if 'GITHUB_OUTPUT' in os.environ and Path(os.environ['GITHUB_OUTPUT']).is_file():
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            if len(value.splitlines()) > 1:
                delimiter = generate_delimiter()
                f.write(f'{name}<<{delimiter}\n')
                f.write(value)

                if not value.endswith('\n'):
                    f.write('\n')
                f.write(f'{delimiter}\n')
            else:
                f.write(f'{name}={value}\n')
    else:
        sys.stdout.write(f'::set-output name={name}::{value}\n')

def mask(value: str) -> None:
    for line in value.splitlines():
        sys.stdout.write(f'::add-mask::{line}\n')
