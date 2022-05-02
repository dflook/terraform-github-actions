from terraform.versions import Version
from terraform_version.tfswitch import parse_tfswitch


def test_parse_tfswitch():
    assert parse_tfswitch('0.13.6') == Version('0.13.6')
    assert parse_tfswitch('''

      0.15.6

    ''') == Version('0.15.6')

    assert parse_tfswitch('1.1.1-cool') == Version('1.1.1-cool')

    try:
        parse_tfswitch('')
    except ValueError:
        pass
    else:
        assert False

    try:
        parse_tfswitch('blahblah')
    except ValueError:
        pass
    else:
        assert False
