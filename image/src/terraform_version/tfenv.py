"""tfenv .terraform-version file support."""

from __future__ import annotations

import os
import re
from typing import Iterable, Optional

from github_actions.debug import debug
from github_actions.inputs import InitInputs
from terraform.versions import latest_version, Version, latest_non_prerelease_version


def parse_tfenv(terraform_version_file: str, versions: Iterable[Version]) -> Version:
    """
    Return the version specified in the terraform version file

    :param terraform_version_file: The contents of a tfenv .terraform-version file.
    :param versions: The available terraform versions
    :return: The terraform version specified by the file
    """

    version = terraform_version_file.strip()

    if version == 'latest':
        return latest_non_prerelease_version(v for v in versions if not v.pre_release)

    if version.startswith('latest:'):
        version_regex = version.split(':', maxsplit=1)[1]

        matched = [v for v in versions if re.search(version_regex, str(v))]

        if not matched:
            raise Exception(f'No terraform versions match regex {version_regex}')

        return latest_version(matched)

    return Version(version)


def try_read_tfenv(inputs: InitInputs, versions: Iterable[Version]) -> Optional[Version]:
    """
    Return the terraform version specified by any .terraform-version file.

    :param inputs: The action inputs
    :param versions: The available terraform versions
    :returns: The terraform version specified by any .terraform-version file, which may be None.
    """

    tfenv_path = os.path.join(inputs.get('INPUT_PATH', '.'), '.terraform-version')

    if not os.path.exists(tfenv_path):
        return None

    try:
        with open(tfenv_path) as f:
            return parse_tfenv(f.read(), versions)
    except Exception as e:
        debug(str(e))

    return None
