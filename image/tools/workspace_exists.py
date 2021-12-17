#!/usr/bin/python3

import sys


def debug(msg: str) -> None:
    for line in msg.splitlines():
        sys.stderr.write(f'::debug::{line}\n')

def workspace_exists(stdin, workspace: str) -> bool:
    for line in stdin:
        debug(line)
        if line.strip().strip('*').strip() == workspace.strip():
            debug('workspace exists')
            return True

    debug('workspace doesn\'t exist')
    return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('No workspace specified')
        exit(1)

    exit(0 if workspace_exists(sys.stdin, sys.argv[1]) else 1)
