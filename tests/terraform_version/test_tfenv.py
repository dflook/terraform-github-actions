from terraform.versions import Version
from terraform_version.tfenv import parse_tfenv

def test_parse_tfenv():
    versions = [
        Version('0.13.6'),
        Version('1.1.8'),
        Version('1.1.9'),
        Version('1.1.7'),
        Version('1.1.0-alpha20210811'),
        Version('1.2.0-alpha20225555')
    ]

    assert parse_tfenv('0.13.6', versions) == Version('0.13.6')
    assert parse_tfenv('''

      0.15.6

    ''', versions) == Version('0.15.6')

    assert parse_tfenv('1.1.1-cool', versions) == Version('1.1.1-cool')

    try:
        parse_tfenv('', versions)
    except ValueError:
        pass
    else:
        assert False

    try:
        parse_tfenv('blahblah', versions)
    except ValueError:
        pass
    else:
        assert False

    assert parse_tfenv('latest', versions) == Version('1.1.9')
    assert parse_tfenv('latest:^1.1', versions) >= Version('1.1.8')
    assert parse_tfenv('latest:1.8', versions) >= Version('1.1.0-alpha20210811')

    try:
        parse_tfenv('latest:^1.8', versions)
    except Exception:
        pass
    else:
        assert False
