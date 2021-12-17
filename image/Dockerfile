FROM danielflook/terraform-github-actions-base:terraform-version

COPY src/ /tmp/src/
COPY setup.py /tmp
RUN pip install /tmp \
 && rm -rf /tmp/src /tmp/setup.py \
 && TERRAFORM_BIN_DIR="/usr/local/bin/terraform" terraform-version 0.9.0 \
 && TERRAFORM_BIN_DIR="/usr/local/bin/terraform" terraform-version 0.12.0

COPY entrypoints/ /entrypoints/
COPY actions.sh /usr/local/actions.sh
COPY workflow_commands.sh /usr/local/workflow_commands.sh

COPY tools/convert_validate_report.py /usr/local/bin/convert_validate_report
COPY tools/github_pr_comment.py /usr/local/bin/github_pr_comment
COPY tools/convert_output.py /usr/local/bin/convert_output
COPY tools/plan_cmp.py /usr/local/bin/plan_cmp
COPY tools/convert_version.py /usr/local/bin/convert_version
COPY tools/workspace_exists.py /usr/local/bin/workspace_exists
COPY tools/compact_plan.py /usr/local/bin/compact_plan
COPY tools/format_tf_credentials.py /usr/local/bin/format_tf_credentials
COPY tools/github_comment_react.py /usr/local/bin/github_comment_react

RUN echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config \
 && echo "IdentityFile /.ssh/id_rsa" >> /etc/ssh/ssh_config \
 && mkdir -p /.ssh

COPY tools/http_credential_actions_helper.py /usr/bin/git-credential-actions
RUN git config --system credential.helper /usr/bin/git-credential-actions \
 && git config --system credential.useHttpPath true \
 && ln -s /usr/bin/git-credential-actions /usr/bin/netrc-credential-actions

LABEL org.opencontainers.image.title="GitHub actions for terraform"
