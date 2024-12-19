from typing import Iterable

from terraform.versions import Version

from opentofu.github import github

def get_opentofu_versions() -> Iterable[Version]:
    """Return the currently available opentofu versions."""

    response = github.paged_get('https://api.github.com/repos/opentofu/opentofu/releases')

    for release in response:
        yield Version(release['tag_name'].lstrip('v'), 'OpenTofu')
