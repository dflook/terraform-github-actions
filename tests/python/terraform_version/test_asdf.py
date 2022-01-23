from __future__ import annotations
from terraform.versions import Version
from terraform_version.asdf import parse_asdf


def test_parse_asdf():
    versions = [
        Version('0.13.6'),
        Version('1.1.8'),
        Version('1.1.9'),
        Version('1.1.7'),
        Version('1.1.0-alpha20210811'),
        Version('1.2.0-alpha20225555')
    ]

    assert parse_asdf('terraform 0.13.6', versions) == Version('0.13.6')
    assert parse_asdf('''
        # comment
      terraform      0.15.6 #basdasd

    ''', versions) == Version('0.15.6')

    assert parse_asdf('terraform 1.1.1-cool', versions) == Version('1.1.1-cool')

    try:
        parse_asdf('', versions)
    except Exception:
        pass
    else:
        assert False

    try:
        parse_asdf('blahblah', versions)
    except Exception:
        pass
    else:
        assert False

    try:
        parse_asdf('terraform blasdasf', versions)
    except Exception:
        pass
    else:
        assert False

    assert parse_asdf('terraform latest', versions) == Version('1.1.9')
