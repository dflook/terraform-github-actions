#!/usr/bin/python3

import json
import sys
from typing import Dict, Iterable
import os.path

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

        summary = diag['summary'].split('\n')[0]
        params = ','.join(f'{k}={v}' for k, v in params.items())
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

    exit(0 if report.get('valid', False) is True else 1)
