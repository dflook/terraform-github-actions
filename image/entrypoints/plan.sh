#!/bin/bash

source /usr/local/actions.sh

set -x

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
(cd $INPUT_PATH && terraform plan -input=false -no-color -detailed-exitcode -lock-timeout=300s -out="$PLAN_DIR/plan.out" $PLAN_ARGS) \
    2>"$PLAN_DIR/error.txt" \
    | $TFMASK \
    | tee /dev/fd/3 \
    | sed '1,/---/d' \
        >"$PLAN_DIR/plan.txt"

readonly TF_EXIT=${PIPESTATUS[0]}
set -e

cat "$PLAN_DIR/error.txt"

if [[ "$GITHUB_EVENT_NAME" == "pull_request" ]]; then
  if [[ "$INPUT_ADD_GITHUB_COMMENT" == "true" ]]; then

    if [[ -z "$GITHUB_TOKEN" ]]; then
      echo "GITHUB_TOKEN environment variable must be set to add GitHub PR comments"
      echo "Either set the GITHUB_TOKEN environment variable, or disable by setting the add_github_comment input to 'false'"
      echo "See https://github.com/dflook/terraform-github-actions/ for details."
      exit 1
    fi

    if [[ $TF_EXIT -eq 1 ]]; then
      STATUS="Failed to generate plan in $(job_markdown_ref)" github_pr_comment plan <"/$PLAN_DIR/error.txt"
    else
      STATUS="Plan generated in $(job_markdown_ref)" github_pr_comment plan <"/$PLAN_DIR/plan.txt"
    fi

  fi

else
  debug_log "Not a pull_request event - not creating a PR comment"
fi

if [[ $TF_EXIT -eq 1 ]]; then
    debug_log "Error running terraform"
    exit 1
fi

if [[ $TF_EXIT -eq 0 ]]; then
    debug_log "No Changes to apply"
    echo "::set-output name=changes::false"

elif [[ $TF_EXIT -eq 2 ]]; then
    debug_log "Changes to apply"
    echo "::set-output name=changes::true"
fi
