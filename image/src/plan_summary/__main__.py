"""
Create plan summary actions outputs

Creates the outputs:
- to_add
- to_change
- to_destroy

Usage:
    plan_summary
"""

from __future__ import annotations

import re
import sys
from github_actions.commands import output

def summary(plan: str) -> dict[str, int]:
    operations = {
        'add': 0,
        'change': 0,
        'destroy': 0,
        'move': None,
        'import': 0
    }

    to_move = 0

    for line in plan.splitlines():
        if re.match(r'  # \S+ has moved to \S+$', line):
            to_move += 1

        if not line.startswith('Plan:'):
            continue

        for op in re.finditer(r'(\d+) to (\w+)', line):
            operations[op[2]] = int(op[1])

    if operations['move'] is None:
        operations['move'] = to_move

    return operations


def main() -> None:
    """Entrypoint for plan_summary"""

    with open(sys.argv[1]) as f:
        plan = f.read()

    for action, count in summary(plan).items():
        output(f'to_{action}', count)


if __name__ == '__main__':
    sys.exit(main())
