#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup
init-backend-workspace
set-plan-args

PLAN_OUT="$STEP_TMP_DIR/plan.out"

function update_comment() {
    if [[ -v TERRAFORM_ACTIONS_GITHUB_TOKEN ]]; then

        if ! github_pr_comment "$@" 2>"$STEP_TMP_DIR/github_pr_comment.stderr"; then
            debug_file "$STEP_TMP_DIR/github_pr_comment.stderr"
        else
            debug_file "$STEP_TMP_DIR/github_pr_comment.stderr"
        fi

    fi
}

update_comment begin-apply

exec 3>&1

function apply() {
    local APPLY_EXIT

    set +e
    if [[ -n "$PLAN_OUT" ]]; then

        # With Terrraform >= 1.10 Ephemeral variables must be specified again in the apply command.
        # Non-ephemeral variables may be specified again, but may not be different from the plan.
        # Terraform < 1.1.0 must not specify any variables when applying a saved plan.

        SAVED_PLAN_VARIABLES=""
        if [[ "$TOOL_PRODUCT_NAME" == "Terraform" ]] && test-terraform-version ">=" "1.10.0"; then
          SAVED_PLAN_VARIABLES="$VARIABLE_ARGS"
        fi

        # shellcheck disable=SC2086
        debug_log $TOOL_COMMAND_NAME apply -input=false -no-color -lock-timeout=300s $PARALLEL_ARG $SAVED_PLAN_VARIABLES $PLAN_OUT
        # shellcheck disable=SC2086
        (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME apply -input=false -no-color -lock-timeout=300s $PARALLEL_ARG $SAVED_PLAN_VARIABLES $PLAN_OUT) \
            2>"$STEP_TMP_DIR/terraform_apply.stderr" \
            | $TFMASK \
            | tee "$STEP_TMP_DIR/terraform_apply.stdout"
        APPLY_EXIT=${PIPESTATUS[0]}
        >&2 cat "$STEP_TMP_DIR/terraform_apply.stderr"

    else
        # There is no plan file to apply, since the remote backend can't produce them.
        # Instead we need to do an auto approved apply using the arguments we would normally use for the plan

        # shellcheck disable=SC2086,SC2016
        debug_log $TOOL_COMMAND_NAME apply -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG $PLAN_ARGS "$(masked-deprecated-vars)" $VARIABLE_ARGS
        # shellcheck disable=SC2086
        (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME apply -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG $PLAN_ARGS $DEPRECATED_VAR_ARGS $VARIABLE_ARGS) \
            2>"$STEP_TMP_DIR/terraform_apply.stderr" \
            | $TFMASK \
            | tee "$STEP_TMP_DIR/terraform_apply.stdout"
        APPLY_EXIT=${PIPESTATUS[0]}
        >&2 cat "$STEP_TMP_DIR/terraform_apply.stderr"

    fi
    set -e

    if [[ "$TERRAFORM_BACKEND_TYPE" == "cloud" || "$TERRAFORM_BACKEND_TYPE" == "remote" ]]; then
        if remote-run-id "$STEP_TMP_DIR/terraform_apply.stdout" "$STEP_TMP_DIR/terraform_apply.stderr" >"$STEP_TMP_DIR/remote-run-id.stdout" 2>"$STEP_TMP_DIR/remote-run-id.stderr"; then
            RUN_ID="$(<"$STEP_TMP_DIR/remote-run-id.stdout")"
            set_output run_id "$RUN_ID"
        else
            debug_log "Failed to get remote run-id"
            debug_file "$STEP_TMP_DIR/remote-run-id.stderr"
        fi
    fi

    if [[ "$TERRAFORM_BACKEND_TYPE" == "cloud" && $APPLY_EXIT -ne 0 ]] && grep -q "Error: Saved plan has no changes" "$STEP_TMP_DIR/terraform_apply.stderr"; then
        # Not really an error then is it?
        APPLY_EXIT=0
        output
        update_comment cloud-no-changes-to-apply "$STEP_TMP_DIR/terraform_output.json"
    elif [[ $APPLY_EXIT -eq 0 ]]; then
        output
        update_comment apply-complete "$STEP_TMP_DIR/terraform_output.json"
    else
        if lock-info "$STEP_TMP_DIR/terraform_apply.stderr"; then
            set_output failure-reason state-locked
        else
            set_output failure-reason apply-failed
        fi
        update_comment error
        exit 1
    fi
}

### Generate a plan

if [[ "$INPUT_PLAN_PATH" != "" ]]; then
  if [[ ! -f "$INPUT_PLAN_PATH" ]]; then
      error_log "Plan file '$INPUT_PLAN_PATH' does not exist"
      exit 1
  fi

  PLAN_OUT=$(realpath "$INPUT_PLAN_PATH")
  PLAN_EXIT=2
else
  plan

  if [[ $PLAN_EXIT -eq 1 ]]; then
      if grep -q "Saving a generated plan is currently not supported" "$STEP_TMP_DIR/terraform_plan.stderr"; then
          set-remote-plan-args
          PLAN_OUT=""

          if [[ "$INPUT_AUTO_APPROVE" == "true" ]]; then
              # The apply will have to generate the plan, so skip doing it now
              PLAN_EXIT=2
          else
              plan
          fi
      fi
  fi

  if [[ $PLAN_EXIT -eq 1 ]]; then
      cat >&2 "$STEP_TMP_DIR/terraform_plan.stderr"

      if lock-info "$STEP_TMP_DIR/terraform_plan.stderr"; then
          set_output failure-reason state-locked
      fi

      update_comment error
      exit 1
  fi

  if [[ -z "$PLAN_OUT" && "$INPUT_AUTO_APPROVE" == "true" ]]; then
      # Since we are doing an auto approved remote apply there is no point in planning beforehand
      # No text_plan_path output for this run
      :
  else
      mkdir -p "$GITHUB_WORKSPACE/$WORKSPACE_TMP_DIR"
      cp "$STEP_TMP_DIR/plan.txt" "$GITHUB_WORKSPACE/$WORKSPACE_TMP_DIR/plan.txt"
      set_output text_plan_path "$WORKSPACE_TMP_DIR/plan.txt"
  fi

  if [[ -n "$PLAN_OUT" ]]; then
      if (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME show -json "$PLAN_OUT") >"$GITHUB_WORKSPACE/$WORKSPACE_TMP_DIR/plan.json" 2>"$STEP_TMP_DIR/terraform_show.stderr"; then
          set_output json_plan_path "$WORKSPACE_TMP_DIR/plan.json"
      else
          debug_file "$STEP_TMP_DIR/terraform_show.stderr"
      fi
  fi
fi

### Apply the plan

if [[ "$TERRAFORM_BACKEND_TYPE" == "cloud" && $PLAN_EXIT -eq 0 ]]; then
    # Terraform cloud will just error if we try to apply a plan with no changes
    echo "No changes to apply"
    output
    update_comment cloud-no-changes-to-apply "$STEP_TMP_DIR/terraform_output.json"

elif [[ "$INPUT_AUTO_APPROVE" == "true" || $PLAN_EXIT -eq 0 ]]; then
    echo "Automatically approving plan"
    apply

else

    if [[ "$GITHUB_EVENT_NAME" != "push" && "$GITHUB_EVENT_NAME" != "pull_request" && "$GITHUB_EVENT_NAME" != "issue_comment" && "$GITHUB_EVENT_NAME" != "pull_request_review_comment" && "$GITHUB_EVENT_NAME" != "pull_request_target" && "$GITHUB_EVENT_NAME" != "pull_request_review" && "$GITHUB_EVENT_NAME" != "repository_dispatch" ]]; then
        echo "Could not fetch plan from the PR - $GITHUB_EVENT_NAME event does not relate to a pull request. You can generate and apply a plan automatically by setting the auto_approve input to 'true'"
        exit 1
    fi

    if [[ ! -v TERRAFORM_ACTIONS_GITHUB_TOKEN ]]; then
        echo "GITHUB_TOKEN environment variable must be set to get plan approval from a PR"
        echo "Either set the GITHUB_TOKEN environment variable or automatically approve by setting the auto_approve input to 'true'"
        echo "See https://github.com/dflook/terraform-github-actions/ for details."
        exit 1
    fi

    if [[ "$INPUT_PLAN_PATH" != "" ]]; then
        if github_pr_comment approved-binary "$PLAN_OUT"; then
          apply
        else
          exit 1
        fi
    else
        if github_pr_comment approved "$STEP_TMP_DIR/plan.txt"; then
          apply
        else
          exit 1
        fi
    fi

fi
