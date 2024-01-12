"""
Module for downloading opentofu executables.
"""

from __future__ import annotations

import os.path
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Tuple
from urllib.request import urlretrieve
from urllib.error import HTTPError
from zipfile import ZipFile

from github_actions.debug import debug

if TYPE_CHECKING:
    from terraform.versions import Version

from terraform.download import DownloadError, get_platform, get_arch


def get_checksums(version: Version, checksum_dir: Path) -> Path:
    """
    Ensure we have the checksums in the checksum dir

    Checksum files must have a valid signature file
    """

    checksums_path = Path(checksum_dir, f'tofu_{version}_SHA256SUMS')
    signature_path = Path(checksum_dir, f'tofu_{version}_SHA256SUMS.gpgsig')

    os.makedirs(checksum_dir, exist_ok=True)

    if not signature_path.exists():
        signature_url = f'https://github.com/opentofu/opentofu/releases/download/v{version}/tofu_{version}_SHA256SUMS.gpgsig'
        debug(f'Downloading signature from {signature_url}')

        try:
            urlretrieve(
                signature_url,
                signature_path
            )
        except HTTPError as http_error:
            if http_error.code == 404:
                if not version.pre_release:
                    raise DownloadError(f'Could not download signature file for {version} - does this version exist?')
            else:
                raise

    if not checksums_path.exists():
        checksum_url = f'https://github.com/opentofu/opentofu/releases/download/v{version}/tofu_{version}_SHA256SUMS'
        debug(f'Downloading checksums from {checksum_url}')

        try:
            urlretrieve(
                checksum_url,
                checksums_path
            )
        except HTTPError as http_error:
            if http_error.code == 404:
                raise DownloadError(f'Could not download checksums for {version} - does this version exist?')
            raise

    if signature_path.exists():
        try:
            subprocess.run(
                ['gpg', '--verify', signature_path, checksums_path],
                check=True,
                env={'GNUPGHOME': '/root/.gnupg'} | os.environ
            )
        except subprocess.CalledProcessError:
            raise DownloadError(f'Could not verify checksums signature for {version}')

    return checksums_path


def download_archive(version: Version, cache_dir: Path) -> Tuple[Path, str]:
    """
    Download the zip file for the given version of opentofu.

    The return value is the path to the zip file
    """

    archive_path = Path(cache_dir, f'tofu_{version}_{get_platform()}_{get_arch()}.zip')

    if os.path.exists(archive_path):
        return cache_dir, f'tofu_{version}_{get_platform()}_{get_arch()}.zip'

    archive_url = f'https://github.com/opentofu/opentofu/releases/download/v{version}/tofu_{version}_{get_platform()}_{get_arch()}.zip'
    debug(f'Downloading archive from {archive_url}')
    os.makedirs(cache_dir, exist_ok=True)

    try:
        urlretrieve(
            archive_url,
            archive_path
        )
    except HTTPError as http_error:
        if http_error.code == 404:
            raise DownloadError(f'Could not download archive for {version} - does this version exist for this platform ({get_platform()}_{get_arch()})?')
        raise

    return cache_dir, f'tofu_{version}_{get_platform()}_{get_arch()}.zip'


def verify_archive(version: Version, cache_dir: Path, archive_name: str, checksum_dir: Path) -> None:
    """
    Verify opentofu zip archive

    :param version: The version of opentofu to verify
    :param cache_dir: The directory the archive is in
    :param archive_name: The name of the archive
    :param checksum_dir: The directory the checksum file can be found in
    """

    def get_checksum():
        """
        Get the checksum for specified archive from the checksums file
        """
        for line in Path(checksum_dir, f'tofu_{version}_SHA256SUMS').read_bytes().splitlines():
            if archive_name.encode() in line:
                return line + b'\n'
        raise RuntimeError('Checksum not found')

    try:
        subprocess.run(
            ['shasum', '--algorithm', '256', '--check', '--strict'],
            check=True,
            cwd=cache_dir,
            input=get_checksum()
        )
    except subprocess.CalledProcessError:
        raise DownloadError(f'Could not verify integrity of opentofu executable for {version}')

def get_archive(version: Version, cache_dirs: list[Path]) -> Tuple[Path, str]:
    """
    Get the zip archive path for a opentofu version
    """

    assert len(cache_dirs) > 0

    for cache_dir in cache_dirs:

        archive_path = Path(cache_dir, f'tofu_{version}_{get_platform()}_{get_arch()}.zip')
        if archive_path.is_file():
            return cache_dir, f'tofu_{version}_{get_platform()}_{get_arch()}.zip'

    return download_archive(version, cache_dir)


def get_executable(version: Version) -> Path:
    """
    Get the path to the specified opentofu executable.

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
    verify_archive(version, cache_dir, archive_name, checksum_dir)

    executable_dir = os.environ.get('STEP_TEMP_DIR', f'/tmp/tofu_{version}')

    Path(executable_dir, 'tofu').unlink(missing_ok=True)
    with ZipFile(Path(cache_dir, archive_name)) as f:
        f.extract('tofu', executable_dir)

    executable_path = Path(executable_dir, 'tofu')

    os.chmod(executable_path, 755)

    return executable_path
