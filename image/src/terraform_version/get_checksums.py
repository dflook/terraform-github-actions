import os
import sys
from pathlib import Path

from opentofu.versions import get_opentofu_versions
from opentofu.download import get_checksums as get_opentofu_checksums
from terraform.download import get_checksums
from terraform.versions import get_terraform_versions


def main() -> None:

    checksum_dir = Path(os.environ.get('TERRAFORM_BIN_CHECKSUM_DIR', '.terraform-bin-dir'))

    for version in get_terraform_versions():
        if version.pre_release:
            continue
        sys.stdout.write(f'Getting checksums for Terraform {version}\n')
        get_checksums(version, checksum_dir)

    for version in get_opentofu_versions():
        sys.stdout.write(f'Getting checksums for OpenTofu {version}\n')
        get_opentofu_checksums(version, checksum_dir)
