FROM danielflook/terraform-github-actions-base:latest

COPY entrypoints/ /entrypoints/
COPY actions.sh /usr/local/actions.sh

COPY tools/convert_validate_report.py /usr/local/bin/convert_validate_report
COPY tools/github_pr_comment.py /usr/local/bin/github_pr_comment
COPY tools/latest_terraform_version.py /usr/local/bin/latest_terraform_version
COPY tools/convert_output.py /usr/local/bin/convert_output
COPY tools/plan_cmp.py /usr/local/bin/plan_cmp
COPY tools/convert_version.py /usr/local/bin/convert_version
COPY tools/workspace_exists.py /usr/local/bin/workspace_exists
COPY tools/compact_plan.py /usr/local/bin/compact_plan

LABEL org.opencontainers.image.title="GitHub actions for terraform"
