#!/usr/bin/python3

import sys

def workspace_exists(stdin, workspace: str) -> bool:
    for line in stdin:
        if line.strip().strip('*').strip() == workspace.strip():
            return True

    return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('No workspace specified')
        exit(1)

    exit(0 if workspace_exists(sys.stdin, sys.argv[1]) else 1)
