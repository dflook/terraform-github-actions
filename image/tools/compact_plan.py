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
            line.startswith('Error')
        ):
            plan = True

        if plan:
            yield line
        else:
            buffer.append(line)

    if not plan and buffer:
        yield from buffer


if __name__ == '__main__':
    for line in compact_plan(sys.stdin.readlines()):
        sys.stdout.write(line)
