#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup
init-backend-workspace
set-plan-args

PLAN_OUT="$STEP_TMP_DIR/plan.out"

if [[ -v TERRAFORM_ACTIONS_GITHUB_TOKEN ]]; then
    update_status ":orange_circle: Applying plan in $(job_markdown_ref)"
fi

exec 3>&1

function apply() {
    local APPLY_EXIT

    set +e
    if [[ -n "$PLAN_OUT" ]]; then
        # shellcheck disable=SC2086
        debug_log terraform apply -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG $PLAN_OUT
        # shellcheck disable=SC2086
        (cd "$INPUT_PATH" && terraform apply -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG $PLAN_OUT) \
            2>"$STEP_TMP_DIR/terraform_apply.stderr" \
            | $TFMASK
        APPLY_EXIT=${PIPESTATUS[0]}
        >&2 cat "$STEP_TMP_DIR/terraform_apply.stderr"
    else
        # There is no plan file to apply, since the remote backend can't produce them.
        # Instead we need to do an auto approved apply using the arguments we would normally use for the plan

        # shellcheck disable=SC2086
        debug_log terraform apply -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG '$PLAN_ARGS'  # don't expand plan args
        # shellcheck disable=SC2086
        (cd "$INPUT_PATH" && terraform apply -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG $PLAN_ARGS) \
            2>"$STEP_TMP_DIR/terraform_apply.stderr" \
            | $TFMASK \
            | tee "$STEP_TMP_DIR/terraform_apply.stdout"
        APPLY_EXIT=${PIPESTATUS[0]}
        >&2 cat "$STEP_TMP_DIR/terraform_apply.stderr"

        if remote-run-id "$STEP_TMP_DIR/terraform_apply.stdout" >"$STEP_TMP_DIR/remote-run-id.stdout" 2>"$STEP_TMP_DIR/remote-run-id.stderr"; then
            RUN_ID="$(<"$STEP_TMP_DIR/remote-run-id.stdout")"
            set_output run_id "$RUN_ID"
        else
            debug_log "Failed to get remote run-id"
            debug_file "$STEP_TMP_DIR/remote-run-id.stderr"
        fi
    fi
    set -e

    if [[ $APPLY_EXIT -eq 0 ]]; then
        update_status ":white_check_mark: Plan applied in $(job_markdown_ref)"
    else
        if lock-info "$STEP_TMP_DIR/terraform_apply.stderr"; then
            set_output failure-reason state-locked
        else
            set_output failure-reason apply-failed
        fi
        update_status ":x: Error applying plan in $(job_markdown_ref)"
        exit 1
    fi
}

### Generate a plan

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

    update_status ":x: Error applying plan in $(job_markdown_ref)"
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
    if (cd "$INPUT_PATH" && terraform show -json "$PLAN_OUT") >"$GITHUB_WORKSPACE/$WORKSPACE_TMP_DIR/plan.json" 2>"$STEP_TMP_DIR/terraform_show.stderr"; then
        set_output json_plan_path "$WORKSPACE_TMP_DIR/plan.json"
    else
        debug_file "$STEP_TMP_DIR/terraform_show.stderr"
    fi
fi

### Apply the plan

if [[ "$INPUT_AUTO_APPROVE" == "true" || $PLAN_EXIT -eq 0 ]]; then
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

    if github_pr_comment approved "$STEP_TMP_DIR/plan.txt"; then
      apply
    else
      exit 1
    fi

fi

output
