"""Module for downloading terraform executables."""

from __future__ import annotations

import os.path
import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.request import urlretrieve
from zipfile import ZipFile

from github_actions.debug import debug

if TYPE_CHECKING:
    from terraform.versions import Version


def get_platform() -> str:
    """Return terraform's idea of the current platform name."""

    p = sys.platform
    if p.startswith('freebsd'):
        return 'freebsd'
    elif p.startswith('linux'):
        return 'linux'
    elif p.startswith('win32'):
        return 'windows'
    elif p.startswith('openbsd'):
        return 'openbsd'
    elif p.startswith('darwin'):
        return 'darwin'

    raise Exception(f'Unknown platform {p}')


def get_arch() -> str:
    """Return terraforms idea of the current architecture."""

    a = platform.machine()
    if a in ['x86_64', 'amd64']:
        return 'amd64'
    elif a in ['i386', 'i686', 'x86']:
        return '386'
    elif a.startswith('armv8') or a.startswith('aarch64'):
        return 'arm64'
    elif a.startswith('arm'):
        return 'arm'

    raise Exception(f'Unknown arch {a}')


def download_version(version: Version, target_dir: Path) -> Path:
    """
    Download the executable for the given version of terraform.

    The return value is the path to the executable
    """

    terraform_path = Path(target_dir, 'terraform')

    if os.path.exists(terraform_path):
        return terraform_path

    debug(f'Downloading terraform {version}')

    local_filename, headers = urlretrieve(
        f'https://releases.hashicorp.com/terraform/{version}/terraform_{version}_{get_platform()}_{get_arch()}.zip',
        f'/tmp/terraform_{version}_linux_amd64.zip'
    )

    with ZipFile(local_filename) as f:
        f.extract('terraform', target_dir)

    os.chmod(terraform_path, 755)

    return Path(os.path.abspath(terraform_path))


def get_executable(version: Version) -> Path:
    """
    Get the path to the specified terraform executable.

    Executables may be in any of the directories in TERRAFORM_BIN_DIR.
    If executable doesn't exist, download it to the last directory in TERRAFORM_BIN_DIR.
    Cache dirs are specified in the TERRAFORM_BIN_DIR env var as ':' separated paths.
    The default is .terraform-bin-dir in the current directory.

    The return value is the path to the executable
    """

    cache_dirs = os.environ.get('TERRAFORM_BIN_DIR', '.terraform-bin-dir').split(':')

    download_dir = None

    for tf_dir in cache_dirs:
        download_dir = Path(tf_dir, f'terraform_{version}')
        terraform_path = os.path.join(download_dir, 'terraform')
        if os.path.isfile(terraform_path):
            return Path(os.path.abspath(terraform_path))

    assert download_dir is not None

    return download_version(version, download_dir)
