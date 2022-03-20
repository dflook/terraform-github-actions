"""
Wraps python-hcl
"""
from typing import Optional

import hcl2  # type: ignore
import sys
import subprocess
from pathlib import Path

from github_actions.debug import debug


def try_load(path: Path) -> dict:
    try:
        with open(path) as f:
            return hcl2.load(f)
    except:
        return {}

def is_loadable(path: Path) -> bool:
    try:
        subprocess.run(
            [sys.executable, '-m', 'terraform.hcl', path],
            timeout=10
        )
    except subprocess.TimeoutExpired:
        # We found a file that won't parse :(
        return False
    except:
        # If we get an exception, we can still try and load it.
        return True

    return False

def load(path: Path) -> Optional[dict]:
    if is_loadable(path):
        return try_load(path)

    debug(f'Unable to load {path}')
    return {}

def loads(hcl: str) -> Optional[dict]:

    tmp_path = Path('/tmp/load_test.hcl')

    with open(tmp_path, 'w') as f:
        f.write(hcl)

    if is_loadable(tmp_path):
        return hcl2.loads(hcl)

    debug('Unable to load hcl')
    return {}

if __name__ == '__main__':
    try_load(Path(sys.argv[1]))
