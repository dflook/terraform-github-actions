import sys
from typing import Any


def output(name: str, value: Any) -> None:
    sys.stdout.write(f'::set-output name={name}::{value}\n')
