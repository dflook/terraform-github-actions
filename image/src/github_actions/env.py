"""GitHub action environment variables."""

from __future__ import annotations

from typing import TypedDict


class ActionsEnv(TypedDict):
    """Environment variables expected by these actions."""
    TERRAFORM_CLOUD_TOKENS: str
    TERRAFORM_SSH_KEY: str
    TERRAFORM_PRE_RUN: str
    TERRAFORM_HTTP_CREDENTIALS: str
    TERRAFORM_VERSION: str
    TERRAFORM_ACTIONS_GITHUB_TOKEN: str


class GithubEnv(TypedDict):
    """Environment variables that are set by the actions runner."""
    GITHUB_API_URL: str
    GITHUB_GRAPHQL_URL: str
    GITHUB_TOKEN: str
    GITHUB_EVENT_PATH: str
    GITHUB_EVENT_NAME: str
    GITHUB_REPOSITORY: str
    GITHUB_SHA: str
    GITHUB_REF_TYPE: str
    GITHUB_REF: str
    GITHUB_WORKSPACE: str
