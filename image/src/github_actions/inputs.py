"""
Typed Action input classes
"""

from __future__ import annotations

from typing import TypedDict


class InitInputs(TypedDict):
    """Common input variables for actions the need to initialize terraform"""
    INPUT_PATH: str
    INPUT_WORKSPACE: str
    INPUT_BACKEND_CONFIG: str
    INPUT_BACKEND_CONFIG_FILE: str


class PlanInputs(InitInputs):
    """Common input variables for actions that generate a plan"""
    INPUT_VARIABLES: str
    INPUT_VAR: str
    INPUT_VAR_FILE: str
    INPUT_PARALLELISM: str


class Plan(PlanInputs):
    """Input variables for the plan action"""
    INPUT_LABEL: str
    INPUT_TARGET: str
    INPUT_REPLACE: str
    INPUT_ADD_GITHUB_COMMENT: str


class Apply(InitInputs):
    """Input variables for the terraform-apply action"""
    INPUT_LABEL: str
    INPUT_TARGET: str
    INPUT_REPLACE: str
    INPUT_AUTO_APPROVE: str


class Check(PlanInputs):
    """Input variables for the terraform-check action"""


class Destroy(PlanInputs):
    """Input variables for the terraform-destroy action"""


class DestroyWorkspace(PlanInputs):
    """Input variables for the terraform-destroy-workspace action"""


class Fmt(TypedDict):
    """Input variables for the terraform-fmt action"""
    INPUT_PATH: str


class FmtCheck(TypedDict):
    """Input variables for the terraform-fmt-check action"""
    INPUT_PATH: str


class Version(TypedDict):
    """Input variables for the terraform-version action"""
    INPUT_PATH: str


class NewWorkspace(InitInputs):
    """Input variables for the terraform-new-workspace action"""


class Output(InitInputs):
    """Input variables for the terraform-output action"""


class RemoteState(TypedDict):
    """Input variables for the terraform-remote-state action"""
    INPUT_BACKEND_TYPE: str
    INPUT_WORKSPACE: str
    INPUT_BACKEND_CONFIG: str
    INPUT_BACKEND_CONFIG_FILE: str


class Validate(TypedDict):
    """Input variables for the terraform-validate action"""
    INPUT_PATH: str
    INPUT_WORKSPACE: str
