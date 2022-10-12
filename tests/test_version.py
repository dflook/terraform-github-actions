import os

from convert_version import convert_version, convert_version_from_json, Output

from terraform.cloud import get_workspaces, new_workspace, delete_workspace


def test_convert_version():
    tf_version_output = 'Terraform v0.12.28'
    expected = [
        Output('terraform', '0.12.28')
    ]

    assert list(convert_version(tf_version_output)) == expected

def test_convert_old_version():
    tf_version_output = 'Terraform v0.11.14'
    expected = [
        Output('terraform', '0.11.14')
    ]

    assert list(convert_version(tf_version_output)) == expected

def test_convert_with_provider():
    tf_version_output = '''Terraform v0.12.28
+ provider.random v2.2.0'''

    expected = [
        Output('terraform', '0.12.28'),
        Output('random', '2.2.0')
    ]

    assert list(convert_version(tf_version_output)) == expected

def test_convert_with_multiple_providers():
    tf_version_output = '''Terraform v0.12.28
+ provider.acme v1.5.0
+ provider.random v2.2.0
'''

    expected = [
        Output('terraform', '0.12.28'),
        Output('acme', '1.5.0'),
        Output('random', '2.2.0')
    ]

    assert list(convert_version(tf_version_output)) == expected

def test_convert_0_13_providers():
    tf_version_output = '''Terraform v0.13.0
+ provider registry.terraform.io/terraform-providers/acme v1.5.0    
+ provider registry.terraform.io/hashicorp/random v2.2.0
'''

    expected = [
        Output('terraform', '0.13.0'),
        Output('acme', '1.5.0'),
        Output('random', '2.2.0')
    ]

    assert list(convert_version(tf_version_output)) == expected

def test_convert_0_13_json_providers():
    tf_version_output = {
      "terraform_version": "0.13.0",
      "terraform_revision": "",
      "provider_selections": {
        "registry.terraform.io/hashicorp/random": "2.2.0",
        "registry.terraform.io/terraform-providers/acme": "2.5.3"
      },
      "terraform_outdated": True
    }

    expected = [
        'Terraform v0.13.0',
        Output('terraform', '0.13.0'),
        '+ provider registry.terraform.io/hashicorp/random v2.2.0',
        Output('random', '2.2.0'),
        '+ provider registry.terraform.io/terraform-providers/acme v2.5.3',
        Output('acme', '2.5.3')
    ]

    assert list(convert_version_from_json(tf_version_output)) == expected
