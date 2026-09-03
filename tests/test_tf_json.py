"""Tests for reading terraform modules written in JSON syntax."""

import json
from pathlib import Path

import hcl2
import pytest

from github_pr_comment.backend_config import read_module_backend_config
from terraform import tf_json
from terraform.module import (
    get_backend_type,
    get_cloud_config,
    get_remote_backend_config,
    get_sensitive_variables,
    get_version_constraints,
)
from terraform.versions import Constraint

S3 = {'bucket': 'b', 'key': 'k', 'region': 'eu-west-1'}
SENSITIVE = {'type': 'string', 'sensitive': True}


def load(tmp_path: Path, body) -> dict:
    """Write the body as a tf.json file and load it with the json parser."""

    path = tmp_path / 'main.tf.json'
    path.write_text(json.dumps(body))
    return tf_json.load(path)


@pytest.mark.parametrize('variable, expected', [
    pytest.param({'api_token': SENSITIVE, 'plain': {'type': 'string'}}, ['api_token'], id='object keyed by name'),
    pytest.param([{'api_token': SENSITIVE}, {'other': SENSITIVE}], ['api_token', 'other'], id='array of objects'),
    pytest.param([{'api_token': SENSITIVE, 'other': SENSITIVE}], ['api_token', 'other'], id='array with several names in one object'),
    pytest.param({'api_token': [SENSITIVE]}, ['api_token'], id='body as an array under the name'),
    pytest.param([{'api_token': [SENSITIVE]}], ['api_token'], id='array of objects with body arrays'),
    pytest.param({'api_token': {'type': 'string', 'sensitive': 'true'}}, ['api_token'], id='quoted string true'),
    pytest.param({'a': {'sensitive': False}, 'b': {'sensitive': 'false'}, 'c': {'type': 'string'}}, [], id='not sensitive'),
])
def test_sensitive_variables(tmp_path, variable, expected):
    module = load(tmp_path, {'variable': variable})

    assert get_sensitive_variables(module) == expected


@pytest.mark.parametrize('terraform, backend_type, backend_config', [
    pytest.param({'backend': {'s3': S3}}, 's3', S3, id='object'),
    pytest.param({'backend': [{'s3': S3}]}, 's3', S3, id='backend as an array'),
    pytest.param({'backend': {'s3': [S3]}}, 's3', S3, id='body as an array under the label'),
    pytest.param({'backend': [{'s3': [S3]}]}, 's3', S3, id='both arrays'),
    pytest.param([{'required_version': '>= 1.5'}, {'backend': {'s3': S3}}], 's3', S3, id='backend in a repeated terraform block'),
    pytest.param([{'required_version': '>= 1.5'}, {'backend': [{'s3': [S3]}]}], 's3', S3, id='arrays at every level'),
    pytest.param({'cloud': {'organization': 'org', 'workspaces': {'name': 'ws'}}}, 'cloud', {'organization': 'org', 'workspaces': [{'name': 'ws'}]}, id='cloud with workspaces object'),
    pytest.param({'cloud': [{'organization': 'org', 'workspaces': [{'name': 'ws'}]}]}, 'cloud', {'organization': 'org', 'workspaces': [{'name': 'ws'}]}, id='cloud array with workspaces array'),
    pytest.param({'backend': {'remote': {'organization': 'org', 'workspaces': {'name': 'ws'}}}}, 'remote', {'organization': 'org', 'workspaces': [{'name': 'ws'}]}, id='remote with workspaces object'),
    pytest.param({'backend': {'remote': {'organization': 'org', 'workspaces': [{'prefix': 'p'}]}}}, 'remote', {'organization': 'org', 'workspaces': [{'prefix': 'p'}]}, id='remote with workspaces array'),
    pytest.param({'backend': {'remote': [{'organization': 'org', 'workspaces': [{'name': 'ws'}]}]}}, 'remote', {'organization': 'org', 'workspaces': [{'name': 'ws'}]}, id='remote body as an array'),
    pytest.param({'required_version': '>= 1.5', 'required_providers': {'aws': {'source': 'hashicorp/aws'}}}, 'local', {}, id='no backend'),
])
def test_backend(tmp_path, terraform, backend_type, backend_config):
    module = load(tmp_path, {'terraform': terraform})

    assert get_backend_type(module) == backend_type
    assert read_module_backend_config(module) == (backend_type, backend_config)


@pytest.mark.parametrize('terraform', [
    pytest.param({'required_version': '>= 1.5'}, id='object'),
    pytest.param([{'required_version': '>= 1.5'}], id='array'),
    pytest.param([{'backend': {'s3': S3}}, {'required_version': '>= 1.5'}], id='second of two terraform blocks'),
])
def test_required_version(tmp_path, terraform):
    module = load(tmp_path, {'terraform': terraform})

    assert get_version_constraints(module) == [Constraint('>= 1.5')]


def test_no_terraform_block(tmp_path):
    module = load(tmp_path, {'variable': {'api_token': SENSITIVE}})

    assert get_version_constraints(module) is None
    assert get_backend_type(module) == 'local'
    assert get_sensitive_variables(module) == ['api_token']


def test_cloud_config(tmp_path):
    module = load(tmp_path, {'terraform': {'cloud': {'hostname': 'tfe.example.com', 'organization': 'org', 'workspaces': {'name': 'ws'}}}})

    config = get_cloud_config(module, tmp_path / 'no-cli-config')

    assert config['hostname'] == 'tfe.example.com'
    assert config['organization'] == 'org'
    assert config['workspaces'] == {'name': 'ws'}


def test_remote_backend_config(tmp_path):
    module = load(tmp_path, {'terraform': {'backend': {'remote': {'hostname': 'tfe.example.com', 'organization': 'org', 'workspaces': {'prefix': 'p'}}}}})

    config = get_remote_backend_config(module, '', '', tmp_path / 'no-cli-config')

    assert config['hostname'] == 'tfe.example.com'
    assert config['organization'] == 'org'
    assert config['workspaces'] == {'prefix': 'p'}


def test_json_and_hcl_parsers_agree(tmp_path):
    """The consumers get the same answers from a tf.json file as from the equivalent HCL."""

    json_module = load(tmp_path, {
        'terraform': {'required_version': '>= 1.5', 'backend': {'s3': S3}},
        'variable': {'api_token': SENSITIVE, 'plain': {'type': 'string'}},
    })
    hcl_module = hcl2.loads('''
terraform {
  required_version = ">= 1.5"
  backend "s3" {
    bucket = "b"
    key    = "k"
    region = "eu-west-1"
  }
}

variable "api_token" {
  type      = string
  sensitive = true
}

variable "plain" {
  type = string
}
''')

    assert get_version_constraints(json_module) == get_version_constraints(hcl_module)
    assert get_backend_type(json_module) == get_backend_type(hcl_module)
    assert read_module_backend_config(json_module) == read_module_backend_config(hcl_module)
    assert get_sensitive_variables(json_module) == get_sensitive_variables(hcl_module)
