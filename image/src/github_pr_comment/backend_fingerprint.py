"""
Backend fingerprinting

Given a completed backend config and environment variables, compute a fingerprint that identifies that backend config.
This disregards any config related to *how* that backend is used.

Combined with the backend type and workspace name, this should uniquely identify a remote state file.

"""
import canonicaljson

from github_actions.debug import debug
from github_pr_comment.backend_config import BackendConfig, BackendType


def fingerprint_remote(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'hostname': backend_config.get('hostname', ''),
        'organization': backend_config.get('organization', ''),
        'workspaces': backend_config.get('workspaces', '')
    }


def fingerprint_cloud(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'hostname': backend_config.get('hostname', ''),
        'organization': backend_config.get('organization', ''),
        'workspaces': backend_config.get('workspaces', '')
    }


def fingerprint_artifactory(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'url': backend_config.get('url') or env.get('ARTIFACTORY_URL', ''),
        'repo': backend_config.get('repo', ''),
        'subpath': backend_config.get('subpath', '')
    }


def fingerprint_azurerm(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'storage_account_name': backend_config.get('storage_account_name', ''),
        'container_name': backend_config.get('container_name', ''),
        'key': backend_config.get('key', ''),
        'environment': backend_config.get('environment') or env.get('ARM_ENVIRONMENT', ''),
        'endpoint': backend_config.get('endpoint') or env.get('ARM_ENDPOINT', ''),
        'resource_group_name': backend_config.get('resource_group_name', ''),
        'msi_endpoint': backend_config.get('msi_endpoint') or env.get('ARM_MSI_ENDPOINT', ''),
        'subscription_id': backend_config.get('subscription_id') or env.get('ARM_SUBSCRIPTION_ID', ''),
        'tenant_id': backend_config.get('tenant_id') or env.get('ARM_TENANT_ID', ''),
    }


def fingerprint_consul(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'path': backend_config.get('path', ''),
        'address': backend_config.get('address') or env.get('CONSUL_HTTP_ADDR', ''),
    }


def fingerprint_cos(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'bucket': backend_config.get('bucket', ''),
        'prefix': backend_config.get('prefix', ''),
        'key': backend_config.get('key', ''),
        'region': backend_config.get('region', '')
    }


def fingerprint_etcd(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'path': backend_config.get('path', ''),
        'endpoints': ' '.join(sorted(backend_config.get('endpoints', '').split(' ')))
    }


def fingerprint_etcd3(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'prefix': backend_config.get('prefix', ''),
        'endpoints': ' '.join(sorted(backend_config.get('endpoints', [])))
    }


def fingerprint_gcs(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'bucket': backend_config.get('bucket', ''),
        'prefix': backend_config.get('prefix', '')
    }


def fingerprint_http(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'address': backend_config.get('address') or env.get('TF_HTTP_ADDRESS', ''),
        'lock_address': backend_config.get('lock_address') or env.get('TF_HTTP_LOCK_ADDRESS', ''),
        'unlock_address': backend_config.get('unlock_address') or env.get('TF_HTTP_UNLOCK_ADDRESS', ''),
    }


def fingerprint_kubernetes(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'secret_suffix': backend_config.get('secret_suffix', ''),
        'namespace': backend_config.get('namespace') or env.get('KUBE_NAMESPACE', ''),
        'host': backend_config.get('host') or env.get('KUBE_HOST', ''),
        'config_path': backend_config.get('config_path') or env.get('KUBE_CONFIG_PATH', ''),
        'config_paths': backend_config.get('config_paths') or env.get('KUBE_CONFIG_PATHS', ''),
        'config_context': backend_config.get('context') or env.get('KUBE_CTX', ''),
        'config_context_cluster': backend_config.get('config_context_cluster') or env.get('KUBE_CTX_CLUSTER', '')
    }


def fingerprint_manta(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'account': backend_config.get('account') or env.get('SDC_ACCOUNT') or env.get('TRITON_ACCOUNT', ''),
        'url': backend_config.get('url') or env.get('MANTA_URL', ''),
        'path': backend_config.get('path', ''),
        'object_name': backend_config.get('object_name', '')
    }


def fingerprint_oss(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'region': backend_config.get('region') or env.get('ALICLOUD_REGION') or env.get('ALICLOUD_DEFAULT_REGION', ''),
        'endpoint': backend_config.get('endpoint') or env.get('ALICLOUD_OSS_ENDPOINT') or env.get('OSS_ENDPOINT', ''),
        'bucket': backend_config.get('bucket', ''),
        'prefix': backend_config.get('prefix', ''),
        'key': backend_config.get('key', ''),
    }


def fingerprint_pg(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'conn_str': backend_config.get('conn_str', ''),
        'schema_name': backend_config.get('schema_name', '')
    }


def fingerprint_s3(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'endpoint': backend_config.get('endpoint') or env.get('AWS_S3_ENDPOINT', ''),
        'bucket': backend_config.get('bucket', ''),
        'workspace_key_prefix': backend_config.get('workspace_key_prefix', ''),
        'key': backend_config.get('key', ''),
    }


def fingerprint_swift(backend_config: BackendConfig, env) -> dict[str, str]:
    return {
        'auth_url': backend_config.get('auth_url') or env.get('OS_AUTH_URL', ''),
        'cloud': backend_config.get('cloud') or env.get('OS_CLOUD', ''),
        'region_name': backend_config.get('region_name') or env.get('OS_REGION_NAME', ''),
        'container': backend_config.get('container', ''),
        'state_name': backend_config.get('state_name', ''),
        'path': backend_config.get('path', ''),
        'tenant_id': backend_config.get('tenant_id') or env.get('OS_TENANT_NAME') or env.get('OS_PROJECT_NAME', ''),
        'project_domain_name': backend_config.get('project_domain_name') or env.get('OS_PROJECT_DOMAIN_NAME', ''),
        'project_domain_id': backend_config.get('project_domain_id') or env.get('OS_PROJECT_DOMAIN_ID', ''),
        'domain_name': backend_config.get('domain_name') or env.get('OS_USER_DOMAIN_NAME') or env.get('OS_PROJECT_DOMAIN_NAME') or env.get('OS_DOMAIN_NAME') or env.get('DEFAULT_DOMAIN'),
        'domain_id': backend_config.get('domain_id') or env.get('OS_PROJECT_DOMAIN_ID', ''),
        'default_domain': backend_config.get('default_domain') or env.get('OS_DEFAULT_DOMAIN', '')
    }


def fingerprint_local(backend_config: BackendConfig, env) -> dict[str, str]:
    fingerprint_inputs = {
        'path': backend_config.get('path', env['INPUT_PATH'])
    }

    if 'workspace_dir' in backend_config:
        fingerprint_inputs['workspace_dir'] = backend_config['workspace_dir']

    return fingerprint_inputs


def fingerprint(backend_type: BackendType, backend_config: BackendConfig, env) -> bytes:
    backends = {
        'remote': fingerprint_remote,
        'artifactory': fingerprint_artifactory,
        'azurerm': fingerprint_azurerm,
        'azure': fingerprint_azurerm,
        'consul': fingerprint_consul,
        'cloud': fingerprint_cloud,
        'cos': fingerprint_cos,
        'etcd': fingerprint_etcd,
        'etcd3': fingerprint_etcd3,
        'gcs': fingerprint_gcs,
        'http': fingerprint_http,
        'kubernetes': fingerprint_kubernetes,
        'manta': fingerprint_manta,
        'oss': fingerprint_oss,
        'pg': fingerprint_pg,
        's3': fingerprint_s3,
        'swift': fingerprint_swift,
        'local': fingerprint_local,
    }

    fingerprint_inputs = backends.get(backend_type, lambda c, e: c)(backend_config, env)

    debug(f'Backend fingerprint includes {fingerprint_inputs.keys()}')

    return canonicaljson.encode_canonical_json(fingerprint_inputs)
