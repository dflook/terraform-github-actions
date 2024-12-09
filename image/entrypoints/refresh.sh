#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup
init-backend-workspace
set-common-plan-args

exec 3>&1

function apply() {
    local APPLY_EXIT

    set +e

    # shellcheck disable=SC2086
    debug_log $TOOL_COMMAND_NAME apply -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG '$PLAN_ARGS'  # don't expand plan args
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME apply -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG $PLAN_ARGS) \
        2>"$STEP_TMP_DIR/terraform_apply.stderr" \
        | $TFMASK \
        | tee "$STEP_TMP_DIR/terraform_apply.stdout"
    APPLY_EXIT=${PIPESTATUS[0]}
    >&2 cat "$STEP_TMP_DIR/terraform_apply.stderr"

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
    elif [[ $APPLY_EXIT -eq 0 ]]; then
        echo "Refresh complete"
    else
        if lock-info "$STEP_TMP_DIR/terraform_apply.stderr"; then
            set_output failure-reason state-locked
        else
            set_output failure-reason refresh-failed
        fi
        exit 1
    fi
}

### Apply the plan
apply
