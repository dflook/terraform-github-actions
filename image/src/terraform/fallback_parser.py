"""
Fallback parsing for hcl files

We only need limited information from Terraform Modules:
- The required_version constraint
- The backend type
- A list of sensitive variable names
- The backend configuration for remote backends and cloud blocks

The easiest way to get this information is to parse the HCL files directly.
This doesn't always work if our parser fails, or the files are malformed.

This fallback 'parser' does the stupidest thing that might work to get the information we need.

TODO: The backend configuration is not yet implemented.
"""

import re
from pathlib import Path
from typing import Optional

from github_actions.debug import debug


def get_required_version(body: str) -> Optional[str]:
    """Get the required_version constraint string from a tf file"""

    if version := re.search(r'required_version\s*=\s*"(.+)"', body):
        return version.group(1)

def get_backend_type(body: str) -> Optional[str]:
    """Get the backend type from a tf file"""

    if backend := re.search(r'backend\s*"(.+)"', body):
        return backend.group(1)

    if backend := re.search(r'backend\s+(.*)\s*{', body):
        return backend.group(1).strip()

    if re.search(r'cloud\s+\{', body):
        return 'cloud'

def get_sensitive_variables(body: str) -> list[str]:
    """Get the sensitive variable names from a tf file"""

    variables = []

    found = False

    for line in reversed(body.splitlines()):
        if re.search(r'sensitive\s*=\s*true', line, re.IGNORECASE) or re.search(r'sensitive\s*=\s*"true"', line, re.IGNORECASE):
            found = True
            continue

        if found and (variable := re.search(r'variable\s*"(.+)"', line)):
            variables.append(variable.group(1))
            found = False

        if found and (variable := re.search(r'variable\s+(.+)\{', line)):
            variables.append(variable.group(1))
            found = False

    return variables

def parse(path: Path) -> dict:
    debug(f'Attempting to parse {path} with fallback parser')
    body = path.read_text()

    module = {}

    if constraint := get_required_version(body):
        module['terraform'] = [{
            'required_version': constraint
        }]

    if backend_type := get_backend_type(body):
        if 'terraform' not in module:
            module['terraform'] = []

        if backend_type == 'cloud':
            module['terraform'].append({'cloud': [{}]})
        else:
            module['terraform'].append({'backend': [{backend_type:{}}]})

    if sensitive_variables := get_sensitive_variables(body):
        module['variable'] = []
        for variable in sensitive_variables:
            module['variable'].append({
                variable: {
                    'sensitive': True
                }
            })

    return module

if __name__ == '__main__':
    from pprint import pprint
    pprint(parse(Path('tests/workflows/test-validate/hard-parse/main.tf')))
