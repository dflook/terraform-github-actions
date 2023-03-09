"""tfswitch .tfswitchrc file support."""

from __future__ import annotations

import os
from typing import Optional

from github_actions.debug import debug
from github_actions.inputs import InitInputs
from terraform.versions import Version


def parse_tfswitch(tfswitch: str) -> Version:
    """
    Return the terraform version specified by a tfswitch file

    :param tfswitch: The contents of a .tfswitchrc file
    :return: The terraform version specified by the file
    """

    return Version(tfswitch.strip())


def try_read_tfswitch(inputs: InitInputs) -> Optional[Version]:
    """
    Return the terraform version specified by any .tfswitchrc file.

    :param inputs: The action inputs
    :returns: The terraform version specified by the file, which may be None.
    """

    tfswitch_path = os.path.join(inputs.get('INPUT_PATH', '.'), '.tfswitchrc')

    if not os.path.exists(tfswitch_path):
        return None

    try:
        with open(tfswitch_path) as f:
            return parse_tfswitch(f.read())
    except Exception as e:
        debug(str(e))

    return None
