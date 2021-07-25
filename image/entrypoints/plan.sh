#!/bin/bash

source /usr/local/actions.sh

debug
setup
init-backend
select-workspace
set-plan-args

PLAN_DIR=$HOME/$GITHUB_RUN_ID-$(random_string)
rm -rf "$PLAN_DIR"
mkdir -p "$PLAN_DIR"

exec 3>&1

set +e
(cd "$INPUT_PATH" && terraform plan -input=false -no-color -detailed-exitcode -lock-timeout=300s $PLAN_ARGS) \
    2>"$PLAN_DIR/error.txt" \
    | $TFMASK \
    | tee /dev/fd/3 \
    | compact_plan \
        >"$PLAN_DIR/plan.txt"

readonly TF_EXIT=${PIPESTATUS[0]}
set -e

cat "$PLAN_DIR/error.txt"

if [[ "$GITHUB_EVENT_NAME" == "pull_request" || "$GITHUB_EVENT_NAME" == "issue_comment" || "$GITHUB_EVENT_NAME" == "pull_request_review_comment" || "$GITHUB_EVENT_NAME" == "pull_request_target" || "$GITHUB_EVENT_NAME" == "pull_request_review" ]]; then
  if [[ "$INPUT_ADD_GITHUB_COMMENT" == "true" || "$INPUT_ADD_GITHUB_COMMENT" == "changes-only" ]]; then

    if [[ -z "$GITHUB_TOKEN" ]]; then
      echo "GITHUB_TOKEN environment variable must be set to add GitHub PR comments"
      echo "Either set the GITHUB_TOKEN environment variable, or disable by setting the add_github_comment input to 'false'"
      echo "See https://github.com/dflook/terraform-github-actions/ for details."
      exit 1
    fi

    if [[ $TF_EXIT -eq 1 ]]; then
      enable_workflow_commands
      STATUS="Failed to generate plan in $(job_markdown_ref)" github_pr_comment plan <"/$PLAN_DIR/error.txt"
      disable_workflow_commands
    else

      if [[ $TF_EXIT -eq 0 ]]; then
        TF_CHANGES=false
      else # [[ $TF_EXIT -eq 2 ]]
        TF_CHANGES=true
      fi

      enable_workflow_commands
      TF_CHANGES=$TF_CHANGES STATUS="Plan generated in $(job_markdown_ref)" github_pr_comment plan <"/$PLAN_DIR/plan.txt"
      disable_workflow_commands
    fi

  fi

else
  debug_log "Not a pull_request, issue_comment, pull_request_target, pull_request_review or pull_request_review_comment event - not creating a PR comment"
fi

if [[ $TF_EXIT -eq 1 ]]; then
    debug_log "Error running terraform"
    exit 1

elif [[ $TF_EXIT -eq 0 ]]; then
    debug_log "No Changes to apply"
    set_output changes false

elif [[ $TF_EXIT -eq 2 ]]; then
    debug_log "Changes to apply"
    set_output changes true
fi
