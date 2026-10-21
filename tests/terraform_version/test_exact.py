from typing import cast

from github_actions.env import ActionsEnv
from github_actions.inputs import InitInputs
from terraform_version.env import try_read_exact_env
from terraform_version.exact import exact_required_version, try_get_exact_version
from terraform.hcl import loads


def env(**kwargs) -> ActionsEnv:
    return cast(ActionsEnv, kwargs)


def inputs(path) -> InitInputs:
    return cast(InitInputs, {'INPUT_PATH': str(path)})


def module(path, required_version=None, backend='s3'):
    body = 'terraform {\n'
    if required_version is not None:
        body += f'  required_version = "{required_version}"\n'
    if backend is not None:
        body += f'  backend "{backend}" {{}}\n'
    body += '}\n'
    (path / 'main.tf').write_text(body)
    # A file that cannot name a version, and so should never be parsed.
    (path / 'other.tf').write_text('resource "null_resource" "example" {}\n')
    return path


# --- the module's own pin -----------------------------------------------------

def test_an_exact_required_version_is_taken():
    assert str(exact_required_version(loads('terraform { required_version = "1.16.3" }'))) == '1.16.3'


def test_a_pinned_pre_release_is_exact():
    assert str(exact_required_version(loads('terraform { required_version = "1.6.0-alpha3" }'))) == '1.6.0-alpha3'


def test_constraints_are_left_to_the_usual_resolution():
    for constraint in ['~> 1.16.0', '>= 1.0.0', '< 2.0.0', '1.16', '>= 1.0.0, < 2.0.0', '!= 1.16.3']:
        assert exact_required_version(loads(f'terraform {{ required_version = "{constraint}" }}')) is None, constraint


def test_no_required_version():
    assert exact_required_version(loads('terraform { backend "s3" {} }')) is None


def test_product_follows_the_action():
    assert exact_required_version(loads('terraform { required_version = "1.6.0" }'), opentofu=True).product == 'OpenTofu'


# --- precedence ---------------------------------------------------------------

def test_the_pin_is_used_when_nothing_outranks_it(tmp_path):
    module(tmp_path, '1.16.3')
    assert str(try_get_exact_version(inputs(tmp_path), env())) == '1.16.3'


def test_a_remote_backend_is_left_alone(tmp_path):
    # The remote workspace's version outranks required_version.
    module(tmp_path, '1.16.3', backend='remote')
    assert try_get_exact_version(inputs(tmp_path), env()) is None


def test_a_cloud_block_is_left_alone(tmp_path):
    (tmp_path / 'main.tf').write_text('terraform {\n  required_version = "1.16.3"\n  cloud {}\n}\n')
    assert try_get_exact_version(inputs(tmp_path), env()) is None


def test_version_files_outrank_the_environment(tmp_path):
    module(tmp_path, required_version=None)
    (tmp_path / '.terraform-version').write_text('1.5.0\n')
    assert try_get_exact_version(inputs(tmp_path), env(TERRAFORM_VERSION='1.16.3')) is None


def test_tfswitchrc_outranks_the_environment(tmp_path):
    module(tmp_path, required_version=None)
    (tmp_path / '.tfswitchrc').write_text('1.5.0\n')
    assert try_get_exact_version(inputs(tmp_path), env(TERRAFORM_VERSION='1.16.3')) is None


def test_tool_versions_outranks_the_environment(tmp_path):
    nested = tmp_path / 'module'
    nested.mkdir()
    module(nested, required_version=None)
    (tmp_path / '.tool-versions').write_text('terraform 1.5.0\n')
    assert try_get_exact_version(inputs(nested), env(TERRAFORM_VERSION='1.16.3')) is None


def test_the_pin_outranks_the_environment(tmp_path):
    module(tmp_path, '1.16.3')
    assert str(try_get_exact_version(inputs(tmp_path), env(TERRAFORM_VERSION='1.2.3'))) == '1.16.3'


def test_the_environment_is_the_fallback(tmp_path):
    module(tmp_path, required_version=None)
    assert str(try_get_exact_version(inputs(tmp_path), env(TERRAFORM_VERSION='1.16.3'))) == '1.16.3'


def test_nothing_names_a_version(tmp_path):
    module(tmp_path, required_version=None)
    assert try_get_exact_version(inputs(tmp_path), env()) is None


def test_a_constraint_in_the_environment_is_not_exact(tmp_path):
    module(tmp_path, required_version=None)
    assert try_get_exact_version(inputs(tmp_path), env(TERRAFORM_VERSION='>= 1.0.0')) is None


# --- the environment half -----------------------------------------------------

def test_a_list_beginning_with_a_version_is_not_exact():
    # Version() reads a prefix, so this is the case that needs a full match.
    assert try_read_exact_env(env(TERRAFORM_VERSION='1.16.3, <2.0.0')) is None


def test_surrounding_whitespace_is_ignored():
    assert str(try_read_exact_env(env(TERRAFORM_VERSION=' 1.16.3\n'))) == '1.16.3'


def test_the_other_products_variable_is_not_used():
    assert try_read_exact_env(env(OPENTOFU_VERSION='1.6.0')) is None
    assert try_read_exact_env(env(TERRAFORM_VERSION='1.16.3'), opentofu=True) is None
