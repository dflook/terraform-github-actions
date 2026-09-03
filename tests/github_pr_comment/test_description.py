import json

from github_pr_comment.__main__ import format_description
from terraform.module import load_module, get_sensitive_variables


def plan_inputs(path, variables):
    return {
        'INPUT_PATH': str(path),
        'INPUT_WORKSPACE': 'default',
        'INPUT_LABEL': '',
        'INPUT_DESTROY': 'false',
        'INPUT_REFRESH': 'true',
        'INPUT_TARGET': '',
        'INPUT_REPLACE': '',
        'INPUT_BACKEND_CONFIG': '',
        'INPUT_BACKEND_CONFIG_FILE': '',
        'INPUT_VAR_FILE': '',
        'INPUT_VARIABLES': variables,
    }


def test_json_sensitive_variable_is_masked(tmp_path, monkeypatch):
    """A variable declared sensitive in a .tf.json file has its value masked in the PR comment."""

    monkeypatch.delenv('OPENTOFU', raising=False)
    (tmp_path / 'variables.tf.json').write_text(json.dumps({
        'variable': {
            'api_token': {'type': 'string', 'sensitive': True},
            'region': {'type': 'string'},
        }
    }))

    inputs = plan_inputs(tmp_path, 'api_token = "example-sensitive-value"\nregion = "eu-west-1"')
    description = format_description(inputs, get_sensitive_variables(load_module(tmp_path)))

    assert 'example-sensitive-value' not in description
    assert 'api_token = (sensitive value)' in description
    assert 'region    = "eu-west-1"' in description


def test_tofu_json_sensitive_variable_is_masked(tmp_path, monkeypatch):
    """A variable declared sensitive in a .tofu.json file has its value masked in the PR comment."""

    monkeypatch.setenv('OPENTOFU', 'true')
    (tmp_path / 'variables.tofu.json').write_text(json.dumps({
        'variable': {
            'api_token': {'type': 'string', 'sensitive': True},
        }
    }))

    inputs = plan_inputs(tmp_path, 'api_token = "example-sensitive-value"')
    description = format_description(inputs, get_sensitive_variables(load_module(tmp_path)))

    assert 'example-sensitive-value' not in description
    assert 'api_token = (sensitive value)' in description
