# hadolint ignore=DL3007
FROM danielflook/terraform-github-actions-base:trixie

ARG TARGETARCH

ARG FETCH_CHECKSUMS
ARG VERSION=99.0.0

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

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
