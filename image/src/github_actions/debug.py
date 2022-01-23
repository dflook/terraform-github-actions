"""Actions debug logging"""

import sys


def debug(msg: str) -> None:
    """Add a message to the actions debug log."""

    for line in msg.splitlines():
        sys.stderr.write(f'::debug::{line}\n')
