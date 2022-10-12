#!/usr/bin/python3

import json
import os.path
import sys
from typing import Dict, Iterable
from github_actions.commands import output


def relative_to_base(file_path: str, base_path: str):
    return os.path.normpath(os.path.join(base_path, file_path))

def convert_to_github(report: Dict, base_path: str) -> Iterable[str]:
    for diag in report['diagnostics']:

        params = {}

        if 'range' in diag:
            if 'filename' in diag['range']:
                params['file'] = relative_to_base(diag['range']['filename'], base_path)
            if 'start' in diag['range']:
                params['line'] = diag['range']['start']['line']
                params['col'] = diag['range']['start']['column']
            if 'end' in diag['range']:
                params['endLine'] = diag['range']['end']['line']
                params['endColumn'] = diag['range']['end']['column']

        summary = diag['summary'].split('\n')[0]
        params = ','.join(f'{k}={v}' for k, v in params.items())

        if summary == 'Module not installed':
            # This is most likely because other errors prevented init from running properly, and not an error in itself.
            continue

        yield f"::{diag['severity']} {params}::{summary}"


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <base_path> <tf_output.json')

    try:
        report = json.load(sys.stdin)
        if not isinstance(report, dict):
            raise Exception('Unable to parse report')
    except:
        exit(1)

    for line in convert_to_github(report, sys.argv[1]):
        print(line)

    if report.get('valid', False) is True:
        exit(0)
    else:
        output('failure-reason', 'validate-failed')
        exit(1)
