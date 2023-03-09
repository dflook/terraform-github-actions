import os
import shutil
import subprocess

import hcl2
import pytest

from terraform.download import get_executable, get_arch
from terraform.versions import Version, apply_constraints, Constraint
from terraform_version.remote_state import try_guess_state_version, get_backend_constraints

arm64_versions = [
    '1.4.0',
    '1.3.9',
    '1.3.8',
    '1.3.7',
    '1.3.6',
    '1.3.5',
    '1.3.4',
    '1.3.3',
    '1.3.2',
    '1.3.1',
    '1.3.0',
    '1.2.9',
    '1.2.8',
    '1.2.7',
    '1.2.6',
    '1.2.5',
    '1.2.4',
    '1.2.3',
    '1.2.2',
    '1.2.1',
    '1.2.0',
    '1.1.9',
    '1.1.8',
    '1.1.7',
    '1.1.6',
    '1.1.5',
    '1.1.4',
    '1.1.3',
    '1.1.2',
    '1.1.1',
    '1.1.0',
    '1.0.11',
    '1.0.10',
    '1.0.9',
    '1.0.8',
    '1.0.7',
    '1.0.6',
    '1.0.5',
    '1.0.4',
    '1.0.3',
    '1.0.2',
    '1.0.1',
    '1.0.0',
    '0.15.5',
    '0.15.4',
    '0.15.3',
    '0.15.2',
    '0.15.1',
    '0.15.0',
    '0.14.11',
    '0.14.10',
    '0.14.9',
    '0.14.8',
    '0.14.7',
    '0.14.6',
    '0.14.5',
    '0.14.4',
    '0.14.3',
    '0.14.2',
    '0.14.1',
    '0.14.0',
    '0.13.7',
    '0.13.6',
    '0.13.5',
]

terraform_versions = arm64_versions + [
    '0.13.4',
    '0.13.3',
    '0.13.2',
    '0.13.1',
    '0.13.0',
    '0.12.31',
    '0.12.30',
    '0.12.29',
    '0.12.28',
    '0.12.27',
    '0.12.26',
    '0.12.25',
    '0.12.24',
    '0.12.23',
    '0.12.21',
    '0.12.20',
    '0.12.19',
    '0.12.18',
    '0.12.17',
    '0.12.16',
    '0.12.15',
    '0.12.14',
    '0.12.13',
    '0.12.12',
    '0.12.11',
    '0.12.10',
    '0.12.9',
    '0.12.8',
    '0.12.7',
    '0.12.6',
    '0.12.5',
    '0.12.4',
    '0.12.3',
    '0.12.2',
    '0.12.1',
    '0.12.0',
    '0.11.15',
    '0.11.14',
    '0.11.13',
    '0.11.12',
    '0.11.11',
    '0.11.10',
    '0.11.9',
    '0.11.8',
    '0.11.7',
    '0.11.6',
    '0.11.5',
    '0.11.4',
    '0.11.3',
    '0.11.2',
    '0.11.1',
    '0.11.0',
    '0.10.8',
    '0.10.7',
    '0.10.6',
    '0.10.5',
    '0.10.4',
    '0.10.3',
    '0.10.2',
    '0.10.1',
    '0.10.0',
    "0.9.11",
    "0.9.10",
    "0.9.9",
    "0.9.8",
    "0.9.7",
]

@pytest.fixture(scope='module', params=["0.9.7", "0.11.8", "1.1.2", "1.3.0", "1.4.0"] if get_arch() == 'amd64' else ["0.13.5", "0.14.0", "1.1.2", "1.3.0", "1.4.0"])
def state_version(request):
    terraform_version = Version(request.param)
    terraform_path = get_executable(terraform_version)

    module_dir = os.path.join(os.getcwd(), '.terraform-state', str(terraform_version))
    os.makedirs(module_dir, exist_ok=True)

    with open(os.path.join(module_dir, 'main.tf'), 'w') as f:
        backend_tf = '''
terraform {
    backend "s3" {
        bucket = "terraform-github-actions"
        key    = "test_remote_state_s3_''' + str(terraform_version) + '''"
        region = "eu-west-2"
        dynamodb_table = "terraform-github-actions"
    }
}
        '''

        f.write(backend_tf + '''

output "hello" { 
    value = "hello" 
}
        ''')

    # Here we go
    result = subprocess.run(
        [terraform_path, 'init'],
        env=os.environ | {'TF_INPUT': 'false'},
        capture_output=True,
        cwd=module_dir
    )
    print(f'{result.args=}')
    print(f'{result.returncode=}')
    print(f'{result.stdout.decode()=}')
    print(f'{result.stderr.decode()=}')
    assert result.returncode == 0

    result = subprocess.run(
        [terraform_path, 'apply'] + (['-auto-approve'] if terraform_version >= Version('0.10.0') else []),
        env=os.environ | {'TF_INPUT': 'false'},
        capture_output=True,
        cwd=module_dir
    )
    print(f'{result.args=}')
    print(f'{result.returncode=}')
    print(f'{result.stdout.decode()=}')
    print(f'{result.stderr.decode()=}')
    assert result.returncode == 0

    shutil.rmtree(os.path.join(module_dir, '.terraform'), ignore_errors=True)

    yield terraform_version, backend_tf

    shutil.rmtree(module_dir, ignore_errors=True)

def test_state(state_version):

    terraform_version, backend_tf = state_version

    module = hcl2.loads(backend_tf)

    initial_candidates = apply_constraints(
        sorted(Version(v) for v in terraform_versions),
        get_backend_constraints(module, {})
    )

    if get_arch() == 'arm64':
        initial_candidates = apply_constraints(
            initial_candidates,
            [Constraint('>= 0.13.5')]
        )

    assert try_guess_state_version(
        {
            'INPUT_BACKEND_CONFIG': '',
            'INPUT_BACKEND_CONFIG_FILE': '',
            'INPUT_WORKSPACE': 'default'
        },
        module,
        versions=initial_candidates
    ) == terraform_version
