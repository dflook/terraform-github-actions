#!/usr/bin/python3

import sys


def compact_plan(input):
    plan = False
    buffer = []

    for line in input:

        if not plan and (
            line.startswith('Terraform used the selected providers') or
            line.startswith('An execution plan has been generated and is shown below') or
            line.startswith('No changes') or
            line.startswith('Error') or
            line.startswith('Changes to Outputs:') or
            line.startswith('Terraform will perform the following actions:')
        ):
            plan = True

        if plan:
            if not (line.startswith('Releasing state lock. This may take a few moments...')
                    or line.startswith('Acquiring state lock. This may take a few moments...')):
                yield line
        else:
            buffer.append(line)

    if not plan and buffer:
        yield from buffer


if __name__ == '__main__':
    for line in compact_plan(sys.stdin.readlines()):
        sys.stdout.write(line)
