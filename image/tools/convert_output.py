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

        else:
            # complex type

            value = json.dumps(output["value"], separators=(",", ":"))

            if output['sensitive'] is True:
                yield f'::add-mask::{value}'

            yield f'::set-output name={name}::{value}'

if __name__ == '__main__':

    input_string = sys.stdin.read()
    try:
        outputs = json.loads(input_string)
        if not isinstance(outputs, dict):
            raise Exception('Unable to parse outputs')
    except:
        sys.stderr.write(input_string)
        raise

    for line in convert_to_github(outputs):
        print(line)

    exit(0)
