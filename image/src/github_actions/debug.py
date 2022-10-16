"""Actions debug logging"""

import sys


def debug(msg: str) -> None:
    """Add a message to the actions debug log."""

    for line in msg.splitlines():
        sys.stderr.write(f'::debug::{line}\n')

def warning(msg: str) -> None:
    """Add a warning message to the workflow log."""

    for line in msg.splitlines():
        sys.stderr.write(f'::warning::{line}\n')
