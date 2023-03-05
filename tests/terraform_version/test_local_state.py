import os
import shutil
import subprocess
from pathlib import Path

import pytest

from terraform.download import get_executable
from terraform.versions import Version
from terraform_version.local_state import read_local_state

terraform_versions = [
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
    '0.10.0'
]


@pytest.fixture(scope='module', params=["0.13.6", "1.1.2"])
def local_state_version(request):
    terraform_version = Version(request.param)
    terraform_path = get_executable(Version(request.param))

    module_dir = Path(os.getcwd(), '.local_state_version', str(terraform_version))
    os.makedirs(module_dir, exist_ok=True)

    with open(os.path.join(module_dir, 'main.tf'), 'w') as f:
        f.write('''
        output "hello" { value = "hello" }
        ''')

    # Here we go
    result = subprocess.run(
        [terraform_path, 'init'],
        env={'TF_INPUT': 'false'},
        capture_output=True,
        cwd=module_dir
    )
    assert result.returncode == 0
    result = subprocess.run(
        [terraform_path, 'apply', '-auto-approve'],
        env={'TF_INPUT': 'false'},
        capture_output=True,
        cwd=module_dir
    )
    assert result.returncode == 0

    shutil.rmtree(os.path.join(module_dir, '.terraform'), ignore_errors=True)

    yield module_dir, terraform_version

    shutil.rmtree(module_dir, ignore_errors=True)


def test_state(local_state_version):
    module_dir, terraform_version = local_state_version
    assert read_local_state(module_dir) == terraform_version
