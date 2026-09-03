import json
from pathlib import Path

from terraform.hcl import loads
from terraform.module import get_sensitive_variables, files_in_module, load_module


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


def test_files_in_module_terraform_json(tmp_path, monkeypatch):
    monkeypatch.delenv('OPENTOFU', raising=False)
    for name in ['main.tf', 'vars.tf.json', 'v1.2.tf.json', 'ignored.tofu', 'ignored.tofu.json', 'ignored.json', 'nope']:
        (tmp_path / name).touch()

    assert {f.name for f in files_in_module(tmp_path)} == {'main.tf', 'vars.tf.json', 'v1.2.tf.json'}


def test_files_in_module_tofu_json(tmp_path, monkeypatch):
    monkeypatch.setenv('OPENTOFU', 'true')
    for name in [
        'main.tf', 'vars.tf.json', 'v1.2.tf.json',
        'pair.tf.json', 'pair.tofu.json',  # tofu.json shadows tf.json with the same base name
        'native.tf', 'native.tofu',        # tofu shadows tf with the same base name
        'mixed.tf.json', 'mixed.tofu',     # no shadowing between the native and json forms
        'ignored.json', 'nope',
    ]:
        (tmp_path / name).touch()

    assert {f.name for f in files_in_module(tmp_path)} == {
        'main.tf', 'vars.tf.json', 'v1.2.tf.json',
        'pair.tofu.json',
        'native.tofu',
        'mixed.tf.json', 'mixed.tofu',
    }


def test_load_module_merges_hcl_and_json(tmp_path, monkeypatch):
    monkeypatch.delenv('OPENTOFU', raising=False)
    (tmp_path / 'variables.tf').write_text('''
variable "hcl_secret" {
  type      = string
  sensitive = true
}
''')
    (tmp_path / 'extra.tf.json').write_text(json.dumps({'variable': {'json_secret': {'type': 'string', 'sensitive': True}}}))

    assert set(get_sensitive_variables(load_module(tmp_path))) == {'hcl_secret', 'json_secret'}


def test_load_tofu_json_sensitive_variable(tmp_path, monkeypatch):
    monkeypatch.setenv('OPENTOFU', 'true')
    (tmp_path / 'variables.tofu.json').write_text(json.dumps({'variable': {'api_token': {'type': 'string', 'sensitive': True}}}))
    (tmp_path / 'main.tofu').write_text('''
resource "terraform_data" "example" {
  input = var.api_token
}
''')

    assert {f.name for f in files_in_module(tmp_path)} == {'variables.tofu.json', 'main.tofu'}
    assert get_sensitive_variables(load_module(tmp_path)) == ['api_token']


def test_load_module_ignores_malformed_json(tmp_path, monkeypatch):
    monkeypatch.delenv('OPENTOFU', raising=False)
    (tmp_path / 'good.tf.json').write_text(json.dumps({'variable': {'good_secret': {'sensitive': True}}}))
    (tmp_path / 'broken.tf.json').write_text('{not json')
    (tmp_path / 'list.tf.json').write_text('[1, 2]')
    (tmp_path / 'wrong-types.tf.json').write_text(json.dumps({'variable': 'nope', 'terraform': 5}))

    assert get_sensitive_variables(load_module(tmp_path)) == ['good_secret']
