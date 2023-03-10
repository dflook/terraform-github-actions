from pathlib import Path
from subprocess import CalledProcessError
from urllib.error import HTTPError

from terraform.versions import Version
from terraform.download import get_checksums, download_archive, verify_archive, DownloadError

import tempfile
import os

def test_get_checksums():

    with tempfile.TemporaryDirectory() as tempdir:
        # Assume correct signature
        checksums_path = get_checksums(Version('0.9.7'), tempdir)
        assert checksums_path.is_file()

        # tamper with the signature
        os.rename(Path(tempdir, 'terraform_0.9.7_SHA256SUMS.72D7468F.sig'),
                  Path(tempdir, 'terraform_0.11.8_SHA256SUMS.72D7468F.sig'))
        try:
            get_checksums(Version('0.11.8'), tempdir)
        except DownloadError as download_error:
            assert str(download_error) == 'Could not verify checksums signature for 0.11.8'
        else:
            raise AssertionError('No exception was raised for invalid signature')

        # No such signature
        try:
            get_checksums(Version('1.1.100'), tempdir)
        except DownloadError as download_error:
            assert str(download_error) == 'Could not download signature file for 1.1.100 - does this version exist?'
        else:
            raise AssertionError('No exception was raised for no signature found')

def test_verify_archive():

    with tempfile.TemporaryDirectory() as tempdir:
        # Assume correct checksum
        version = Version('0.13.6')
        get_checksums(version, tempdir)
        archive_dir, archive_name = download_archive(version, tempdir)
        verify_archive(version, archive_dir, archive_name, tempdir)

        # No checksum found
        version = Version('0.14.0')
        os.rename(Path(tempdir, 'terraform_0.13.6_SHA256SUMS'),
                  Path(tempdir, 'terraform_0.14.0_SHA256SUMS'))
        archive_dir, archive_name = download_archive(version, tempdir)

        try:
            verify_archive(version, archive_dir, archive_name, tempdir)
        except RuntimeError:
            pass
        else:
            raise AssertionError('No exception was raised for checksum not found')

        # Incorrect checksum
        Path(tempdir, 'terraform_0.14.0_SHA256SUMS').write_bytes(
            b'53f7bbde44262a32765731553a61dc8e103d49a036c85eacc3f2bdbe9ecf7777  ' + archive_name.encode()
        )

        try:
            verify_archive(version, archive_dir, archive_name, tempdir)
        except DownloadError as download_error:
            assert str(download_error) == 'Could not verify integrity of terraform executable for 0.14.0'
        else:
            raise AssertionError('No exception was raised for incorrect checksum')
