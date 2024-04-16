import hcl2

from terraform.versions import Version
from terraform_version.required_version import get_required_version


def test_required_version():
    expected_backend = hcl2.loads('''
        terraform {
            required_version = "1.0.0"
        }
    ''')

    assert get_required_version(expected_backend, [Version('1.0.0')]) == Version('1.0.0')

def test_required_version_v_prefix():
    expected_backend = hcl2.loads('''
        terraform {
            required_version = "v1.0.0"
        }
    ''')

    assert get_required_version(expected_backend, [Version('1.0.0')]) == Version('1.0.0')

def test_required_version_greater_than():
    expected_backend = hcl2.loads('''
        terraform {
            required_version = ">= 1.8.0"
        }
    ''')

    assert get_required_version(expected_backend, [Version('1.7.0'), Version('1.8.0'), Version('1.8.1')]) == Version('1.8.1')


def test_required_version_greater_than_v_prefix():
    expected_backend = hcl2.loads('''
        terraform {
            required_version = ">= v1.8.0"
        }
    ''')

    assert get_required_version(expected_backend, [Version('1.7.0'), Version('1.8.0'), Version('1.8.1')]) == Version('1.8.1')
