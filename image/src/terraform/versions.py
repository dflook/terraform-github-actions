"""Module for working with Terraform versions and version constraints."""

from __future__ import annotations

import re
from functools import total_ordering
from typing import Any, cast, Iterable, Literal, Optional

import requests

session = requests.Session()

ConstraintOperator = Literal['=', '!=', '>', '>=', '<', '<=', '~>']


@total_ordering
class Version:
    """
    A Terraform version.

    Versions are made up of major, minor & patch numbers, plus an optional pre_release string.
    """

    def __init__(self, version: str):

        match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-(?P<pre_release>[\d\w-]+))?', version)
        if not match:
            raise ValueError(f'Not a valid version {version}')

        self.major = int(match.group(1))
        self.minor = int(match.group(2))
        self.patch = int(match.group(3))
        self.pre_release = match.group(4) or ''

    def __repr__(self) -> str:
        s = f'{self.major}.{self.minor}.{self.patch}'

        if self.pre_release:
            s += f'-{self.pre_release}'

        return s

    def __hash__(self) -> int:
        return hash(self.__repr__())

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            return NotImplemented

        return self.major == other.major and self.minor == other.minor and self.patch == other.patch and self.pre_release == other.pre_release

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Version):
            return NotImplemented

        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        if self.pre_release != other.pre_release:
            if self.pre_release == '':
                return False
            if other.pre_release == '':
                return True
            return self.pre_release < other.pre_release

        return False


class Constraint:
    """A Terraform version constraint."""

    def __init__(self, constraint: str):
        if match := re.match(r'([=!<>~]*)(.*)', constraint.replace(' ', '')):
            self.operator = cast(ConstraintOperator, match.group(1) or '=')
            constraint = match.group(2)
        else:
            raise ValueError(f'Invalid version constraint {constraint}')

        if match := re.match(r'(?P<major>\d+)(?:\.(?P<minor>\d+))?(?:\.(?P<patch>\d+))?(?:-(?P<pre_release>.*))?', constraint):
            self.major = int(match.group('major'))
            self.minor = int(match.group('minor')) if match.group('minor') else None
            self.patch = int(match.group('patch')) if match.group('patch') else None
            self.pre_release = match.group('pre_release') or ''
        else:
            raise ValueError(f'Invalid version constraint {constraint}')

    def __repr__(self) -> str:
        s = f'{self.operator}{self.major}'

        if self.minor is not None:
            s += f'.{self.minor}'

        if self.patch is not None:
            s += f'.{self.patch}'

        if self.pre_release:
            s += f'-{self.pre_release}'

        return s

    def __hash__(self) -> int:
        return hash(self.__repr__())

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Constraint):
            return NotImplemented

        return self.major == other.major and self.minor == other.minor and self.patch == other.patch and self.pre_release == other.pre_release and self.operator == other.operator

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Constraint):
            return NotImplemented

        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return (self.minor or 0) < (other.minor or 0)
        if self.patch != other.patch:
            return (self.patch or 0) < (other.patch or 0)
        if self.pre_release != other.pre_release:
            if self.pre_release == '':
                return False
            if other.pre_release == '':
                return True
            return self.pre_release < other.pre_release

        operator_order = ['<', '<=', '=', '~>', '>=', '>']
        return operator_order.index(self.operator) < operator_order.index(other.operator)

    def is_allowed(self, version: Version) -> bool:
        """Is the given version allowed by this constraint."""

        def compare() -> int:
            """
            Compare this version with the specified other version.

            If this version < other version, the return value is < 0
            If this version > other version, the return value is > 0
            If the versions are the same, the return value is 0
            """

            if version.major != self.major:
                return version.major - self.major
            if version.minor != (self.minor or 0):
                return version.minor - (self.minor or 0)
            if version.patch != (self.patch or 0):
                return version.patch - (self.patch or 0)

            if version.pre_release < self.pre_release:
                return -1
            if version.pre_release > self.pre_release:
                return 1

            return 0

        if self.operator == '=':
            return compare() == 0
        if self.operator == '!=':
            return compare() != 0 and not version.pre_release
        if self.operator == '>':
            return compare() > 0 and not version.pre_release
        if self.operator == '>=':
            return compare() >= 0 and not version.pre_release
        if self.operator == '<':
            return compare() < 0 and not version.pre_release
        if self.operator == '<=':
            return compare() <= 0 and not version.pre_release
        if self.operator == '~>':
            if version.pre_release:
                return False

            if self.minor is None:
                # ~> x
                return version.major >= self.major

            if self.patch is None:
                # ~> x.x
                return version.major == self.major and version.minor >= self.minor

            # ~> x.x.x
            return version.major == self.major and version.minor == self.minor and version.patch >= self.patch

def latest_non_prerelease_version(versions: Iterable[Version]) -> Optional[Version]:
    """Return the latest non prerelease version of the given versions."""

    for v in sorted(versions, reverse=True):
        if not v.pre_release:
            return v

def latest_version(versions: Iterable[Version]) -> Version:
    """Return the latest version of the given versions."""

    return sorted(versions, reverse=True)[0]

def earliest_non_prerelease_version(versions: Iterable[Version]) -> Optional[Version]:
    """Return the earliest non prerelease version of the given versions."""

    for v in sorted(versions):
        if not v.pre_release:
            return v

def earliest_version(versions: Iterable[Version]) -> Version:
    """Return the earliest version of the given versions."""

    return sorted(versions)[0]


def get_terraform_versions() -> Iterable[Version]:
    """Return the currently available terraform versions."""

    response = session.get('https://releases.hashicorp.com/terraform/')
    response.raise_for_status()

    version_regex = re.compile(br'/(\d+\.\d+\.\d+(-[\d\w-]+)?)')

    for version in version_regex.finditer(response.content):
        yield Version(version.group(1).decode())


def apply_constraints(versions: Iterable[Version], constraints: Iterable[Constraint]) -> Iterable[Version]:
    """
    Apply the given version constraints.

    Returns the terraform versions that are allowed by all the given constraints
    """

    for version in versions:
        if all(constraint.is_allowed(version) for constraint in constraints):
            yield version
