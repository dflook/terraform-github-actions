from github_pr_comment.backend_config import read_backend_config_vars, partial_backend_config, complete_config
from terraform.hcl import loads

def test_read_backend_config_vars():
    assert read_backend_config_vars({
        'INPUT_BACKEND_CONFIG_FILE': 'tests/github_pr_comment/test_file.tfvars'
    }) == {'hello': 'world'}

def test_read_partial_backend_config():
    assert partial_backend_config({}) == ('local', {})

    assert partial_backend_config(loads('''
terraform {
  backend aws {}
}
    ''')) == ('aws', {})

    assert partial_backend_config(loads('''
terraform {
  backend aws {
    hello = true
  }
}
    ''')) == ('aws', {'hello': True})

    assert partial_backend_config(loads('''
terraform {
  cloud {
  }
}
    ''')) == ('cloud', {})

    assert partial_backend_config(loads('''
terraform {
  cloud {
    hello = true
  }
}
    ''')) == ('cloud', {'hello': True})

def test_complete_config():
    assert complete_config(
        {
            'INPUT_BACKEND_CONFIG_FILE': 'tests/github_pr_comment/test_file.tfvars'
        },
        {}) == ('local', {'hello': 'world'})

    assert complete_config(
        {
            'INPUT_BACKEND_CONFIG_FILE': 'tests/github_pr_comment/test_file.tfvars'
        },
        loads('''
        terraform {
          backend aws {
          
          }
        }
        ''')) == ('aws', {'hello': 'world'})

    assert complete_config(
        {
            'INPUT_BACKEND_CONFIG_FILE': 'tests/github_pr_comment/test_file.tfvars'
        },
        loads('''
        terraform {
          backend azurerm {
            monkey = true
          }
        }
        ''')) == ('azurerm', {'hello': 'world', 'monkey': True})
