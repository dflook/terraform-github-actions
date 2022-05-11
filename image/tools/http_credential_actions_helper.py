#!/usr/bin/env python3

import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass
class Credential:
    hostname: str
    path: List[str]
    username: str
    password: str


def git_credential(operation: str, attributes: Dict[str, str], credentials: List[Credential]):
    att = attributes.copy()
    sys.stderr.write(repr(att) + '\n')

    if operation != 'get':
        return att

    if att.get('protocol') not in ['http', 'https']:
        return att

    for cred in credentials:
        if att.get('host') != cred.hostname:
            continue

        if 'username' in att and att['username'] != cred.username:
            continue

        if cred.path != split_path(att.get('path', ''))[:len(cred.path)]:
            continue

        # Path matches
        att['username'] = cred.username
        att['password'] = cred.password

        path = '/'.join(cred.path)
        sys.stderr.write(f'Using TERRAFORM_HTTP_CREDENTIALS for {cred.hostname}{f"/{path}" if path else ""}={cred.username}\n')
        break
    else:
        path = att.get('path', '')
        sys.stderr.write(f'No matching credentials found in TERRAFORM_HTTP_CREDENTIALS for {att.get("host")}{f"/{path}" if path else ""}\n')

    return att

def split_path(path: Optional[str]) -> List[str]:
    if path is None:
        return []
    return [segment for segment in path.split('/') if segment]


def read_attributes(att_string: str) -> Dict[str, str]:
    attributes = {}
    for line in att_string.splitlines():
        match = re.match(r'^(.+?)=(.+)$', line)
        if match:
            attributes[match.group(1)] = match.group(2)

    return attributes


def write_attributes(attributes: Dict[str, str]) -> str:
    return '\n'.join(f'{k}={v}' for k, v in attributes.items())


def read_credentials(creds: str) -> Iterable[Credential]:
    for line in creds.splitlines():
        match = re.match(r'(.*?)(/.*?)?=(.*?):(.*)', line.strip())
        if match:
            yield Credential(
                hostname=match.group(1).strip(),
                path=split_path(match.group(2)),
                username=match.group(3).strip(),
                password=match.group(4).strip()
            )

def netrc(credentials: List[Credential]) -> str:
    s = ''
    for cred in credentials:
        s += f'machine {cred.hostname}\n'
        s += f'login {cred.username}\n'
        s += f'password {cred.password}\n'
    return s

def main():
    credentials = list(read_credentials(os.environ.get('TERRAFORM_HTTP_CREDENTIALS', '')))

    if sys.argv[0] == '/usr/bin/netrc-credential-actions':
        sys.stdout.write(netrc(credentials))
    else:
        if len(sys.argv) != 2:
            sys.stderr.write('This must be configured as a git credential helper\n')
            exit(1)

        op = sys.argv[1]

        in_attributes = read_attributes(sys.stdin.read())
        out_attributes = git_credential(op, in_attributes, credentials)
        sys.stdout.write(write_attributes(out_attributes))


if __name__ == '__main__':
    main()
