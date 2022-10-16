from __future__ import annotations
from terraform.versions import Version, earliest_version, latest_version, earliest_non_prerelease_version, latest_non_prerelease_version


def test_latest():
    versions = [
        Version('0.13.6-alpha-23'),
        Version('0.13.6'),
        Version('1.1.8'),
        Version('1.1.9'),
        Version('1.1.7'),
        Version('1.1.0-alpha20210811'),
        Version('1.2.0-alpha20225555'),
        Version('1.2.0-alpha-20220328')
    ]

    assert earliest_version(versions) == Version('0.13.6-alpha-23')
    assert latest_version(versions) == Version('1.2.0-alpha20225555')
    assert earliest_non_prerelease_version(versions) == Version('0.13.6')
    assert latest_non_prerelease_version(versions) == Version('1.1.9')
