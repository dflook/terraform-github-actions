"""
Wraps python-hcl
"""

import hcl2  # type: ignore
import sys
import subprocess
import tempfile
from pathlib import Path

from github_actions.debug import debug
import terraform.fallback_parser


def try_load(path: Path) -> dict:
    try:
        with open(path) as f:
            return hcl2.load(f)
    except Exception as e:
        debug(f'Failed to load {path}')
        debug(str(e))
        return terraform.fallback_parser.parse(Path(path))


def is_loadable(path: Path) -> bool:
    try:
        subprocess.run(
            [sys.executable, '-m', 'terraform.hcl', path],
            timeout=10
        )
    except subprocess.TimeoutExpired:
        debug('TimeoutExpired')
        # We found a file that won't parse :(
        return False
    except Exception:
        # If we get an exception, we can still try and load it.
        return True

    return True


def load(path: Path) -> dict:
    if is_loadable(path):
        return try_load(path)

    debug(f'Unable to load {path}')
    raise ValueError(f'Unable to load {path}')


def loads(hcl: str) -> dict:
    with tempfile.NamedTemporaryFile('w', suffix='.hcl', delete=False) as f:
        f.write(hcl)
        tmp_path = Path(f.name)

    try:
        loadable = is_loadable(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    if loadable:
        try:
            return hcl2.loads(hcl)
        except Exception as e:
            debug('Failed to parse hcl')
            debug(str(e))

    debug('Unable to load hcl')
    raise ValueError('Unable to load hcl')


if __name__ == '__main__':
    try_load(Path(sys.argv[1]))
