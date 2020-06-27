#!/usr/bin/python3

import re
import sys
from typing import Iterable


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

    for provider in re.finditer(r'provider\.(\w+) v(.*)', tf_output):
        yield f'::set-output name={provider.group(1)}::{provider.group(2)}'


if __name__ == '__main__':
    tf_output = sys.stdin.read()

    print(tf_output)

    for line in convert_version(tf_output):
        print(line)
