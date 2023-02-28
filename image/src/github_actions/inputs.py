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


class PlanPrInputs(PlanInputs):
    """Common input variables for actions that use a PR comment"""
    INPUT_LABEL: str
    INPUT_TARGET: str
    INPUT_REPLACE: str
    INPUT_DESTROY: str


class Plan(PlanPrInputs):
    """Input variables for the plan action"""
    INPUT_ADD_GITHUB_COMMENT: str


class Apply(PlanPrInputs):
    """Input variables for the terraform-apply action"""
    INPUT_AUTO_APPROVE: str


class Check(PlanInputs):
    """Input variables for the terraform-check action"""


class Destroy(PlanInputs):
    """Input variables for the terraform-destroy action"""


class DestroyWorkspace(PlanInputs):
    """Input variables for the terraform-destroy-workspace action"""


class Fmt(InitInputs):
    """Input variables for the terraform-fmt action"""


class FmtCheck(InitInputs):
    """Input variables for the terraform-fmt-check action"""


class Version(InitInputs):
    """Input variables for the terraform-version action"""


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


class Validate(InitInputs):
    """Input variables for the terraform-validate action"""
