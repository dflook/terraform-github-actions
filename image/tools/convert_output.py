#!/usr/bin/python3

import json
import sys
from dataclasses import dataclass
from pathlib import Path
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

def read_input(s: str) -> dict:
    """
    If there is a problem connecting to terraform, the output contains junk lines we need to skip over
    """

    # Remove any lines that don't start with a {
    # This is because terraform sometimes outputs junk lines
    # before the JSON output
    lines = s.splitlines()
    while lines and not lines[0].startswith('{'):
        lines.pop(0)

    jstr = '\n'.join(lines)
    return json.loads(jstr)

def write_json_outputs(json_output_path: Path, outputs: Dict):
    """
    Flatten the terraform json output format to a simple dictionary, and write it to a file.
    """

    json_outputs = {name: o['value'] for name, o in outputs.items()}

    with open(json_output_path, 'w') as f:
        json.dump(json_outputs, f, indent=2, sort_keys=True)

if __name__ == '__main__':

    input_string = sys.stdin.read()
    try:
        outputs = read_input(input_string)
        if not isinstance(outputs, dict):
            raise Exception('Unable to parse outputs')
    except:
        sys.stderr.write(input_string)
        raise

    write_json_outputs(Path(sys.argv[1]), outputs)

    for command in convert_to_github(outputs):
        if isinstance(command, Output):
            output(command.name, command.value)
        elif isinstance(command, Mask):
            mask(command.value)

    exit(0)
