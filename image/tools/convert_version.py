#!/usr/bin/python3

import json
import re
import sys
from typing import Dict, Iterable


def convert_version(tf_output: str) -> Iterable[str]:
    """
    Convert terraform version output to GitHub actions output commands

    >>> tf_output = '''
    Terraform v0.12.28
    + provider.acme v1.5.0
    '''
    >>> list(convert_version(tf_output))
    ['::set-output name=terraform::0.12.28',
     '::set-output name=acme::1.5.0']
    """

    tf_version = re.match(r'Terraform v(.*)', tf_output)
    if not tf_version:
        raise ValueError('Unexpected terraform version output')

    yield f'::set-output name=terraform::{tf_version.group(1)}'

    for provider in re.finditer(r'provider[\. ](.+) v(.*)', tf_output):

        provider_name = provider.group(1)
        provider_version = provider.group(2)

        if tf_version.group(1).startswith('0.13'):
            source_address = re.match(r'(.*?)/(.*?)/(.*)', provider_name)
            if source_address:
                provider_name = source_address.group(3)

        yield f'::set-output name={provider_name.strip()}::{provider_version.strip()}'


def convert_version_from_json(tf_output: Dict) -> Iterable[str]:
    """
    Convert terraform version JSON output human readable output and GitHub actions output commands

    >>> tf_output = {
      "terraform_version": "0.13.7",
      "terraform_revision": "",
      "provider_selections": {
        "registry.terraform.io/hashicorp/random": "2.2.0"
      },
      "terraform_outdated": true
    }
    >>> list(convert_version(tf_output))
    ['Terraform v0.13.7',
     '::set-output name=terraform::0.13.7',
     '+ provider registry.terraform.io/hashicorp/random v2.2.0',
     '::set-output name=random::2.2.0']
    """

    yield f'Terraform v{tf_output["terraform_version"]}'
    yield f'::set-output name=terraform::{tf_output["terraform_version"]}'

    for path, version in tf_output['provider_selections'].items():
        name_match = re.match(r'(.*?)/(.*?)/(.*)', path)
        name = name_match.group(3) if name_match else path

        yield f'+ provider {path} v{version}'
        yield f'::set-output name={name}::{version}'


if __name__ == '__main__':
    tf_output = sys.stdin.read()

    try:
        for line in convert_version_from_json(json.loads(tf_output)):
            print(line)
    except:
        print(tf_output)

        for line in convert_version(tf_output):
            print(line)
