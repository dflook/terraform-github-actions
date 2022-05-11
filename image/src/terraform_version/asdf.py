"""asdf .tool-versions file support."""

from __future__ import annotations

import os
import re
from typing import Iterable, Optional

from github_actions.debug import debug
from github_actions.inputs import InitInputs
from terraform.versions import Version, latest_non_prerelease_version


def parse_asdf(tool_versions: str, versions: Iterable[Version]) -> Version:
    """Return the version specified in an asdf .tool-versions file."""

    for line in tool_versions.splitlines():
        if match := re.match(r'^\s*terraform\s+([^\s#]+)', line.strip()):
            if match.group(1) == 'latest':
                return latest_non_prerelease_version(v for v in versions if not v.pre_release)
            return Version(match.group(1))

    raise Exception('No version for terraform found in .tool-versions')


def try_read_asdf(inputs: InitInputs, workspace_path: str, versions: Iterable[Version]) -> Optional[Version]:
    """Return the version from an asdf .tool-versions file if possible."""

    module_path = os.path.abspath(inputs.get('INPUT_PATH', '.'))

    while module_path not in ['/', workspace_path]:
        asdf_path = os.path.join(module_path, '.tool-versions')

        if os.path.isfile(asdf_path):
            try:
                with open(asdf_path) as f:
                    return parse_asdf(f.read(), versions)
            except Exception as e:
                debug(str(e))

        module_path = os.path.dirname(module_path)

    return None
