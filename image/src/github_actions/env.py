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


class GithubEnv(TypedDict):
    """Environment variables set by github actions."""
    GITHUB_WORKSPACE: str
