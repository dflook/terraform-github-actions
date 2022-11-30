from github_pr_comment.backend_config import read_backend_config_files, read_module_backend_config, complete_config, partial_config, read_backend_config_input
from terraform.hcl import loads

def test_read_backend_config_files():
    assert read_backend_config_files({
        'INPUT_BACKEND_CONFIG_FILE': 'tests/github_pr_comment/test_file.tfvars'
    }) == {'hello': 'world'}

def test_read_read_module_backend_config():
    assert read_module_backend_config({}) == ('local', {})

    assert read_module_backend_config(loads('''
terraform {
  backend aws {}
}
    ''')) == ('aws', {})

    assert read_module_backend_config(loads('''
terraform {
  backend aws {
    hello = true
  }
}
    ''')) == ('aws', {'hello': True})

    assert read_module_backend_config(loads('''
terraform {
  cloud {
  }
}
    ''')) == ('cloud', {})

    assert read_module_backend_config(loads('''
terraform {
  cloud {
    hello = true
  }
}
    ''')) == ('cloud', {'hello': True})

def test_read_backend_config_input():
    assert read_backend_config_input(
        {
        'INPUT_BACKEND_CONFIG': '''hello=world,var=test
another=ok'''
        }) == {
            'hello': 'world',
            'var': 'test',
            'another': 'ok'
        }

    assert read_backend_config_input(
        {
        'INPUT_BACKEND_CONFIG': ''
        }) == {}

def test_complete_config():
    assert complete_config(
        {
            'INPUT_BACKEND_CONFIG_FILE': 'tests/github_pr_comment/test_file.tfvars',
            'INPUT_BACKEND_CONFIG': 'from_var=hello'
        },
        {}) == ('local', {'hello': 'world', 'from_var': 'hello'})

    assert complete_config(
        {
            'INPUT_BACKEND_CONFIG_FILE': 'tests/github_pr_comment/test_file.tfvars',
            'INPUT_BACKEND_CONFIG': 'from_var=hello'
        },
        loads('''
        terraform {
          backend aws {
          
          }
        }
        ''')) == ('aws', {'hello': 'world', 'from_var': 'hello'})

    assert complete_config(
        {
            'INPUT_BACKEND_CONFIG_FILE': 'tests/github_pr_comment/test_file.tfvars',
            'INPUT_BACKEND_CONFIG': 'from_var=hello'
        },
        loads('''
        terraform {
          backend azurerm {
            monkey = true
          }
        }
        ''')) == ('azurerm', {'hello': 'world', 'monkey': True, 'from_var': 'hello'})


def test_partial_config():
    assert partial_config(
        {
            'INPUT_BACKEND_CONFIG_FILE': 'tests/github_pr_comment/test_file.tfvars',
            'INPUT_BACKEND_CONFIG': 'from_var=hello'
        },
        {}) == ('local', {'from_var': 'hello'})

    assert partial_config(
        {
            'INPUT_BACKEND_CONFIG_FILE': 'tests/github_pr_comment/test_file.tfvars',
            'INPUT_BACKEND_CONFIG': 'from_var=hello'
        },
        loads('''
        terraform {
          backend aws {

          }
        }
        ''')) == ('aws', {'from_var': 'hello'})

    assert partial_config(
        {
            'INPUT_BACKEND_CONFIG_FILE': 'tests/github_pr_comment/test_file.tfvars',
            'INPUT_BACKEND_CONFIG': 'from_var=hello'
        },
        loads('''
        terraform {
          backend azurerm {
            monkey = true
          }
        }
        ''')) == ('azurerm', {'monkey': True, 'from_var': 'hello'})
