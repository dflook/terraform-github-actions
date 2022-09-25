"""Module for interacting with Terraform Cloud/Enterprise."""

from __future__ import annotations

import datetime
import os
from typing import Iterable, Optional, TypedDict, Any, cast

import requests
from requests import Response

from github_actions.debug import debug
from terraform.module import BackendConfig

session = requests.Session()


class Workspace(TypedDict):
    """A Terraform cloud workspace"""
    id: str
    attributes: dict[str, Any]


class CloudException(Exception):
    """Raised when there is an error interacting with terraform cloud."""

    def __init__(self, msg: str, response: Optional[Response]):
        super().__init__(msg)
        self.response = response


class TerraformCloudApi:
    def __init__(self, host: str, token: str):
        self._host = host
        self._token = token

    def api_request(self, method: str, path: str, /, headers: Optional[dict[str, str]] = None, **kwargs: Any) -> Response:
        if headers is None:
            headers = {}

        headers['Authorization'] = f'Bearer {self._token}'

        path = path.removeprefix('/')

        response = session.request(method, f'https://{self._host}/api/v2/{path}', headers=headers, **kwargs)

        debug(f'terraform cloud request url={response.url}')
        debug(f'terraform cloud {response.status_code=}')

        if response.status_code == 401:
            debug(str(response.content))
            raise CloudException('Terraform cloud operation failed: Unauthorized', response)
        elif response.status_code == 429:
            debug(str(response.content))
            raise CloudException('Terraform cloud rate limit reached', response)
        elif not response.ok:
            debug(response.content.decode())
            raise CloudException(f'Terraform cloud unexpected response code {response.status_code}', response)

        return response

    def get(self, path: str, **kwargs: Any) -> Response:
        return self.api_request('GET', path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Response:
        return self.api_request('DELETE', path, **kwargs)

    def post(self, path: str, body: dict[str, Any], **kwargs: Any) -> Response:
        return self.api_request('POST', path, headers={'Content-Type': 'application/vnd.api+json'}, json=body, **kwargs)

    def paged_get(self, path: str, **kwargs: Any) -> Iterable[Any]:

        page_num = 1
        while page_num is not None:
            response = self.api_request('GET', path, params={'page[size]': 100, 'page[number]': page_num}, **kwargs)

            body = response.json()
            yield from body.get('data', {})

            page_num = body['meta']['pagination']['next-page']

def get_full_workspace_name(backend_config: BackendConfig, workspace_name: str) -> str:

    if 'prefix' in backend_config['workspaces']:
        return backend_config['workspaces']['prefix'] + workspace_name

    elif 'name' in backend_config['workspaces']:
        if backend_config['workspaces']['name'] != workspace_name:
            raise CloudException(f'Only the configured workspace name {backend_config["workspaces"]["name"]!r} can be used, not {workspace_name!r}', None)
        return workspace_name

    else:
        return workspace_name

def get_workspaces(backend_config: BackendConfig) -> Iterable[Workspace]:
    """
    Return the workspaces that match the specified backend config.

    :param: The backend config to get workspaces for.
    :return: The remote workspaces that match the backend config.
    """

    terraform_cloud = TerraformCloudApi(backend_config["hostname"], backend_config['token'])

    for workspace in terraform_cloud.paged_get(
        f'/organizations/{backend_config["organization"]}/workspaces',
    ):

        if 'name' in backend_config['workspaces']:
            if workspace['attributes']['name'] == backend_config['workspaces']['name']:
                yield workspace
        elif 'prefix' in backend_config['workspaces']:
            if workspace['attributes']['name'].startswith(backend_config['workspaces']['prefix']):
                yield workspace
        elif 'tags' in backend_config['workspaces']:
            if all(tag in workspace['attributes']['tag-names'] for tag in backend_config['workspaces']['tags']):
                yield workspace


def new_workspace(backend_config: BackendConfig, workspace_name: str) -> None:
    """
    Create a new terraform cloud workspace.

    :param backend_config: Configuration for the backend to create the workspace in.
    :param workspace_name: The name of the workspace to create.
    :return: The new workspace.
    """

    full_workspace_name = get_full_workspace_name(backend_config, workspace_name)

    attributes = {
        "name": full_workspace_name,
        "resource-count": 0,
        "updated-at": datetime.datetime.utcnow().isoformat() + 'Z',
    }

    if version := os.environ.get('TERRAFORM_VERSION'):
        attributes['terraform-version'] = version

    terraform_cloud = TerraformCloudApi(backend_config["hostname"], backend_config['token'])

    body = {
        'data': {
            'attributes': attributes,
            'type': 'workspaces'
        }
    }

    try:
        response = terraform_cloud.post(f'/organizations/{backend_config["organization"]}/workspaces', body)
    except CloudException as cloud_exception:
        if cloud_exception.response is None:
            raise

        content = cloud_exception.response.json()

        for error in content.get('errors', []):
            if error.get('detail') != 'Name has already been taken':
                raise

            # A workspace with this name already exists
            debug(f'A workspace named {workspace_name!r} already exists')

            if 'tags' not in backend_config['workspaces']:
                # We are done, the workspace exists
                return None

            # For a cloud workspace, check the tags match
            if get_workspace(backend_config, workspace_name):
                # It has the correct tags
                return None

            raise CloudException(
                f'A workspace with the name {workspace_name!r} already exists, but without the correct tags. You must manually migrate this workspace by adding the correct tags.',
                cloud_exception.response
            )

        raise

    workspace: dict[str, Any] = response.json()['data']

    if 'tags' in backend_config['workspaces']:
        terraform_cloud.post(
            f'/workspaces/{workspace["id"]}/relationships/tags',
            body={
                "data": [{
                    "attributes": {
                        "name": tag,
                    },
                    "type": "tags"
                } for tag in sorted(backend_config['workspaces']['tags'])]
            }
        )


def delete_workspace(backend_config: BackendConfig, workspace_name: str) -> None:
    """
    Delete a terraform cloud workspace.

    :param backend_config: Configuration for the backend that contains the workspace.
    :param workspace_name: The name of the workspace to delete.
    """

    full_workspace_name = get_full_workspace_name(backend_config, workspace_name)

    if 'tags' in backend_config['workspaces']:
        # Try to get the workspace to check that it has the correct tags
        if get_workspace(backend_config, workspace_name) is None:
            raise CloudException(f'No such workspace {workspace_name!r} that matches the backend configuration', None)

    terraform_cloud = TerraformCloudApi(backend_config["hostname"], backend_config['token'])

    try:
        terraform_cloud.delete(f'/organizations/{backend_config["organization"]}/workspaces/{full_workspace_name}')
    except CloudException as cloud_exception:
        if cloud_exception.response is not None and cloud_exception.response.status_code == 404:
            raise CloudException(f'No such workspace {workspace_name!r} that matches the backend configuration', cloud_exception.response)
        raise


def get_workspace(backend_config: BackendConfig, workspace_name: str) -> Optional[Workspace]:
    """
    Get a remote workspace.

    :param backend_config: Configuration for the backend that contains the workspace.
    :param workspace_name: The name of the workspace to get.
    :return: The workspace, or None if there is no such workspace
    """

    full_workspace_name = get_full_workspace_name(backend_config, workspace_name)

    terraform_cloud = TerraformCloudApi(backend_config["hostname"], backend_config['token'])

    try:
        response = terraform_cloud.get(
            f'/organizations/{backend_config["organization"]}/workspaces/{full_workspace_name}'
        )
    except CloudException as cloud_exception:
        if cloud_exception.response is not None and cloud_exception.response.status_code == 404:
            return None
        raise

    workspace = response.json()['data']

    if 'tags' in backend_config['workspaces']:
        if not all(tag in workspace['attributes']['tag-names'] for tag in backend_config['workspaces']['tags']):
            return None

    return cast(Workspace, workspace)
