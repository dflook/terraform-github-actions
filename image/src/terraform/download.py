"""
Module for downloading terraform executables.
"""

from __future__ import annotations

import os.path
import platform
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Tuple
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


def get_checksums(version: Version, checksum_dir: Path) -> Path:
    """
    Ensure we have the checksums in the checksum dir

    Checksum files must have a valid signature file
    """

    checksums_path = Path(checksum_dir, f'terraform_{version}_SHA256SUMS')
    signature_path = Path(checksum_dir, f'terraform_{version}_SHA256SUMS.72D7468F.sig')

    if not signature_path.exists():
        debug('Downloading signature')
        os.makedirs(checksum_dir, exist_ok=True)
        urlretrieve(
            f'https://releases.hashicorp.com/terraform/{version}/terraform_{version}_SHA256SUMS.72D7468F.sig',
            signature_path
        )

    if not checksums_path.exists():
        debug('Downloading checksums')
        urlretrieve(
            f'https://releases.hashicorp.com/terraform/{version}/terraform_{version}_SHA256SUMS',
            checksums_path
        )

    subprocess.run(
        ['gpg', '--verify', signature_path, checksums_path],
        check=True,
        env={'GNUPGHOME': '/root/.gnupg'} | os.environ
    )

    return checksums_path


def download_archive(version: Version, cache_dir: Path) -> Tuple[Path, str]:
    """
    Download the zip file for the given version of terraform.

    The return value is the path to the zip file
    """

    archive_path = Path(cache_dir, f'terraform_{version}_{get_platform()}_{get_arch()}.zip')

    if os.path.exists(archive_path):
        return cache_dir, f'terraform_{version}_{get_platform()}_{get_arch()}.zip'

    debug('Downloading archive')
    os.makedirs(cache_dir, exist_ok=True)
    urlretrieve(
        f'https://releases.hashicorp.com/terraform/{version}/terraform_{version}_{get_platform()}_{get_arch()}.zip',
        archive_path
    )

    return cache_dir, f'terraform_{version}_{get_platform()}_{get_arch()}.zip'


def verify_archive(version: Version, cache_dir: Path, checksum_dir: Path) -> None:
    """
    Verify terraform zip archive

    :param version: The version of terraform to verify
    :param cache_dir: The directory the archive is in
    :param checksum_dir: The directory the checksum file can be found in
    """

    subprocess.run(
        ['shasum', '-a', '256', '-c', Path(checksum_dir, f'terraform_{version}_SHA256SUMS').absolute(), '--ignore-missing'],
        check=True,
        cwd=cache_dir
    )


def get_archive(version: Version, cache_dirs: list[Path]) -> Tuple[Path, str]:
    """
    Get the zip archive path for a terraform version
    """

    assert len(cache_dirs) > 0

    for cache_dir in cache_dirs:

        archive_path = Path(cache_dir, f'terraform_{version}_{get_platform()}_{get_arch()}.zip')
        if archive_path.is_file():
            return cache_dir, f'terraform_{version}_{get_platform()}_{get_arch()}.zip'

    return download_archive(version, cache_dir)


def get_executable(version: Version) -> Path:
    """
    Get the path to the specified terraform executable.

    The directories in TERRAFORM_BIN_CACHE_DIR will be searched for the executable as a zip file.
    If the executable doesn't exist it will be downloaded to the last directory in TERRAFORM_BIN_CACHE_DIR.
    Cache dirs are specified in the TERRAFORM_BIN_CACHE_DIR env var as ':' separated paths.
    These directories are untrusted and anything found there will be verified.

    The TERRAFORM_BIN_CHECKSUM_DIR will be searched for checksum and signature files.
    If they are not found they will be downloaded to TERRAFORM_BIN_CHECKSUM_DIR.

    The default for both TERRAFORM_BIN_CACHE_DIR and TERRAFORM_BIN_CHECKSUM_DIR is .terraform-bin-dir in the current directory.

    The return value is the path to the executable
    """

    cache_dirs = [Path(p) for p in os.environ.get('TERRAFORM_BIN_CACHE_DIR', '.terraform-bin-dir').split(':')]
    checksum_dir = Path(os.environ.get('TERRAFORM_BIN_CHECKSUM_DIR', '.terraform-bin-dir'))

    get_checksums(version, checksum_dir)
    cache_dir, archive_name = get_archive(version, cache_dirs)
    verify_archive(version, cache_dir, checksum_dir)

    executable_dir = os.environ.get('STEP_TEMP_DIR', f'/tmp/terraform_{version}')

    Path(executable_dir, 'terraform').unlink(missing_ok=True)
    with ZipFile(Path(cache_dir, archive_name)) as f:
        f.extract('terraform', executable_dir)

    executable_path = Path(executable_dir, 'terraform')

    os.chmod(executable_path, 755)

    return executable_path
