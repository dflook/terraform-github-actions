#!/usr/bin/python3

import json
import sys
from typing import Dict, Iterable


def convert_to_github(outputs: Dict) -> Iterable[str]:
    for name, output in outputs.items():

        if isinstance(output['type'], str):
            # primitive type

            if output['sensitive'] is True:
                yield f'::add-mask::{str(output["value"])}'

            if output['type'] in ['string', 'number']:
                yield f'::set-output name={name}::{output["value"]}'

            if output['type'] == 'bool':
                yield f'::set-output name={name}::{json.dumps(output["value"])}'


if __name__ == '__main__':
    try:
        outputs = json.load(sys.stdin)
        if not isinstance(outputs, dict):
            raise Exception('Unable to parse outputs')
    except:
        exit(1)

    for line in convert_to_github(outputs):
        print(line)

    exit(0)
