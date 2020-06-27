#!/usr/bin/python3

import json
import sys
from typing import Dict, Iterable


def convert_to_github(report: Dict) -> Iterable[str]:
    for diag in report['diagnostics']:

        params = {}

        if 'range' in diag:
            if 'filename' in diag['range']:
                params['file'] = diag['range']['filename']
            if 'start' in diag['range']:
                params['line'] = diag['range']['start']['line']
                params['col'] = diag['range']['start']['column']

        summary = diag['summary'].split('\n')[0]
        params = ','.join(f'{k}={v}' for k, v in params.items())
        yield f"::{diag['severity']} {params}::{summary}"


if __name__ == '__main__':
    try:
        report = json.load(sys.stdin)
        if not isinstance(report, dict):
            raise Exception('Unable to parse report')
    except:
        exit(1)

    for line in convert_to_github(report):
        print(line)

    exit(0 if report.get('valid', False) is True else 1)
