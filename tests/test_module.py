from pathlib import Path

from terraform.hcl import loads
from terraform.module import get_sensitive_variables, files_in_module


def test_get_sensitive_variables():
    module = loads('''
variable hello {
    type = string
}

variable not_secret {
    type = string
    sensitive = false
}

variable secret {
    type = string
    sensitive = true
}

variable super_secret {
    type = string
    sensitive = true
}

''')

    assert get_sensitive_variables(module) == ['secret', 'super_secret']

def test_load_terraform_module():
    assert set(s.name for s in files_in_module(Path('tests/tofu-module'))) == {
        'blah.tf',
        'hello.tf',
    }

def test_load_tofu_module(monkeypatch):
    monkeypatch.setenv('OPENTOFU', 'true')
    assert set(s.name for s in files_in_module(Path('tests/tofu-module'))) == {
        'blah.tf',
        'hello.tofu',
        'tofu-only.tofu'
    }
