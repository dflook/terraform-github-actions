"""
Create plan summary actions outputs

Creates the outputs:
- to_add
- to_change
- to_destroy
- to_move
- to_import
- to_forget
- to_invoke

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
        'import': 0,
        'forget': None,
        'invoke': 0
    }

    to_move = 0
    to_forget = 0

    for line in plan.splitlines():
        if re.match(r'  # \S+ has moved to \S+$', line):
            to_move += 1

        # Terraform doesn't include forgotten resources in the summary line, so count them
        if re.match(r' # \S+ will no longer be managed by Terraform, but will not be destroyed$', line):
            to_forget += 1

        if re.match(r'  # \S+ will be removed from the OpenTofu state but will not be destroyed$', line):
            to_forget += 1

        if not line.startswith('Plan:'):
            continue

        for op in re.finditer(r'(\d+) to (\w+)', line):
            operations[op[2]] = int(op[1])

    if operations['move'] is None:
        operations['move'] = to_move

    if operations['forget'] is None:
        operations['forget'] = to_forget

    return operations


def main() -> None:
    """Entrypoint for plan_summary"""

    with open(sys.argv[1]) as f:
        plan = f.read()

    for action, count in summary(plan).items():
        output(f'to_{action}', count)


if __name__ == '__main__':
    sys.exit(main())
