import os
import sys
from pathlib import Path

from terraform.download import get_checksums
from terraform.versions import get_terraform_versions


def main() -> None:

    checksum_dir = Path(os.environ.get('TERRAFORM_BIN_CHECKSUM_DIR', '.terraform-bin-dir'))

    for version in get_terraform_versions():
        if version.pre_release:
            continue
        sys.stdout.write(f'Getting checksums for {version}\n')
        get_checksums(version, checksum_dir)
