#!/usr/bin/python3

import re
from distutils.version import StrictVersion
from typing import List

import requests

version = re.compile(br'/(\d+\.\d+\.\d+)/')


def get_versions() -> List[StrictVersion]:
    response = requests.get('https://releases.hashicorp.com/terraform/')
    response.raise_for_status()

    versions = [StrictVersion(v.group(1).decode()) for v in version.finditer(response.content)]
    return versions


def latest_version(versions: List[StrictVersion]):
    return str(sorted(versions, reverse=True)[0])


if __name__ == '__main__':
    print(latest_version(get_versions()))


def test_version():
    versions = get_versions()
    print(versions)
    assert StrictVersion('0.12.28') in versions
    assert StrictVersion('0.12.5') in versions
    assert StrictVersion('0.11.14') in versions
