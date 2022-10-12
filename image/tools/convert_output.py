#!/usr/bin/python3

import json
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, Union
from github_actions.commands import output, mask

@dataclass
class Mask:
    value: str

@dataclass
class Output:
    name: str
    value: str

def convert_to_github(outputs: Dict) -> Iterable[Union[Mask, Output]]:
    for name, output in outputs.items():

        if isinstance(output['type'], str):
            # primitive type

            if output['sensitive'] is True:
                yield Mask(str(output["value"]))

            if output['type'] in ['string', 'number']:
                yield Output(name, str(output["value"]))

            if output['type'] == 'bool':
                yield Output(name, json.dumps(output["value"]))

        else:
            # complex type

            value = json.dumps(output["value"], separators=(",", ":"))

            if output['sensitive'] is True:
                yield Mask(value)

            yield Output(name, str(value))

if __name__ == '__main__':

    input_string = sys.stdin.read()
    try:
        outputs = json.loads(input_string)
        if not isinstance(outputs, dict):
            raise Exception('Unable to parse outputs')
    except:
        sys.stderr.write(input_string)
        raise

    for command in convert_to_github(outputs):
        if isinstance(command, Output):
            output(command.name, command.value)
        elif isinstance(command, Mask):
            mask(command.value)

    exit(0)
