# hadolint ignore=DL3007
FROM danielflook/terraform-github-actions-base:latest

ARG TARGETARCH

ARG FETCH_CHECKSUMS
ARG VERSION=99.0.0

# The pip wheel used by `python3 -m venv` also vendors a CA bundle
# Replace it with a copy of the system bundle, updating the wheel RECORD to match
RUN python3 <<'EOF'
import base64, hashlib, re, zipfile
from pathlib import Path

WHEEL = Path('/usr/share/python-wheels/pip-25.1.1-py3-none-any.whl')
RECORD = 'pip-25.1.1.dist-info/RECORD'
CACERT = 'pip/_vendor/certifi/cacert.pem'
bundle = Path('/etc/ssl/certs/ca-certificates.crt').read_bytes()
digest = base64.urlsafe_b64encode(hashlib.sha256(bundle).digest()).rstrip(b'=').decode()

patched = WHEEL.with_suffix('.tmp')

with zipfile.ZipFile(WHEEL) as src, zipfile.ZipFile(patched, 'w') as dst:
    for info in src.infolist():
        data = src.read(info)
        if info.filename == CACERT:
            data = bundle
        elif info.filename == RECORD:
            record, count = re.subn(rf'^{re.escape(CACERT)},[^\r\n]*', f'{CACERT},sha256={digest},{len(bundle)}', data.decode(), flags=re.M)
            assert count == 1, count
            data = record.encode()
        dst.writestr(info, data)

patched.replace(WHEEL)
EOF

# Debian patches pip to use the system CA bundle, so pip's vendored bundles are unused
# Point them at the system bundle anyway so they don't carry stale CAs
RUN python3 -m venv /opt/venv \
 && ln -sf /etc/ssl/certs/ca-certificates.crt /usr/lib/python3/dist-packages/pip/_vendor/certifi/cacert.pem \
 && ln -sf /etc/ssl/certs/ca-certificates.crt /opt/venv/lib/python3.13/site-packages/pip/_vendor/certifi/cacert.pem
ENV PATH="/opt/venv/bin:$PATH"

# Use the system CA bundle (kept current by the base image) instead of certifi
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --no-cache-dir --require-hashes -r /tmp/requirements.txt

COPY src/ /tmp/src/
COPY setup.py /tmp
RUN sed -i "s|version='.*'|version=\'${VERSION}\'|" /tmp/setup.py \
 && pip install --no-cache-dir --no-deps /tmp \
 && rm -rf /tmp/src /tmp/setup.py /tmp/build /tmp/pip-*

RUN if [ "$FETCH_CHECKSUMS" = "yes" ]; then \
  TERRAFORM_BIN_CHECKSUM_DIR="/var/terraform" get-terraform-checksums; \
fi

# TARGETARCH is set by the buildx command, which is used for the release image
# It will not be set when building locally, or when built by GitHub Actions
RUN if [ "$TARGETARCH" = "amd64" ]; then \
      TERRAFORM_BIN_CACHE_DIR="/var/terraform" TERRAFORM_BIN_CHECKSUM_DIR="/var/terraform" terraform-version 0.9.0 \
   && TERRAFORM_BIN_CACHE_DIR="/var/terraform" TERRAFORM_BIN_CHECKSUM_DIR="/var/terraform" terraform-version 0.12.0; \
fi \
 && rm -rf /tmp/terraform_* /usr/local/bin/terraform /usr/local/bin/tofu
RUN if [ "$TARGETARCH" = "arm64" ]; then \
      TERRAFORM_BIN_CACHE_DIR="/var/terraform" TERRAFORM_BIN_CHECKSUM_DIR="/var/terraform" terraform-version 0.13.5; \
fi \
 && rm -rf /tmp/terraform_* /usr/local/bin/terraform /usr/local/bin/tofu

COPY entrypoints/ /entrypoints/
COPY actions.sh /usr/local/actions.sh
COPY workflow_commands.sh /usr/local/workflow_commands.sh

COPY tools/convert_validate_report.py /usr/local/bin/convert_validate_report
COPY tools/convert_output.py /usr/local/bin/convert_output
COPY tools/convert_version.py /usr/local/bin/convert_version
COPY tools/workspace_exists.py /usr/local/bin/workspace_exists
COPY tools/compact_plan.py /usr/local/bin/compact_plan
COPY tools/format_tf_credentials.py /usr/local/bin/format_tf_credentials
COPY tools/github_comment_react.py /usr/local/bin/github_comment_react

COPY tools/http_credential_actions_helper.py /usr/bin/git-credential-actions
RUN git config --system credential.helper /usr/bin/git-credential-actions \
 && git config --system credential.useHttpPath true \
 && ln -s /usr/bin/git-credential-actions /usr/bin/netrc-credential-actions

LABEL org.opencontainers.image.title="GitHub actions for terraform"
