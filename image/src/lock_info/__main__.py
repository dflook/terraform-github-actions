"""
Create an actions output for any lock info

Input arg is a path to a file containing stderr from a terraform command
If any state lock info is found creates a `lock-info` actions output with a json dump of the lock info
and has a zero exit code.

If no state locked error is present, has a nonzero exit

Usage:
    lock-info <TERRAFORM_STDERR_PATH>
"""

import json
import re
import sys
from typing import Iterable, Optional
from github_actions.commands import output

def get_lock_info(stderr: Iterable[str]) -> Optional[dict[str, str]]:
    locked = False
    lock_info_line = False
    lock_info = {}

    for line in stderr:
        if locked is True:
            if lock_info_line:
                if match := re.match(r'^\s+(?P<field>.*?):\s+(?P<value>.*)', line):
                    lock_info[match['field']] = match['value']

            elif line.startswith('Lock Info:'):
                lock_info_line = True

        elif 'Error acquiring the state lock' in line:
            locked = True

    return lock_info if locked else None


def main():
    with open(sys.argv[1]) as f:
        lock_info = get_lock_info(f.readlines())

    if lock_info is None:
        sys.exit(1)

    output('lock-info', json.dumps(lock_info))


if __name__ == '__main__':
    main()
