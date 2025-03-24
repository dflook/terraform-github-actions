#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup
init-backend-workspace
set-variable-args

exec 3>&1

function refresh() {
    local REFRESH_EXIT

    PARALLEL_ARG=""
    if [[ "$INPUT_PARALLELISM" -ne 0 ]]; then
        PARALLEL_ARG="-parallelism=$INPUT_PARALLELISM"
    fi

    REFRESH_ARGS=""
    if [[ -v INPUT_TARGET ]]; then
        if [[ -n "$INPUT_TARGET" ]]; then
            for target in $(echo "$INPUT_TARGET" | tr ',' '\n'); do
                REFRESH_ARGS="$REFRESH_ARGS -target $target"
            done
        fi
    fi

    set +e

    # shellcheck disable=SC2086,SC2016
    debug_log $TOOL_COMMAND_NAME refresh -input=false -no-color -lock-timeout=300s $PARALLEL_ARG $REFRESH_ARGS $VARIABLE_ARGS
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME refresh -input=false -no-color -lock-timeout=300s $PARALLEL_ARG $REFRESH_ARGS $VARIABLE_ARGS) \
        2>"$STEP_TMP_DIR/terraform_refresh.stderr" \
        | tee "$STEP_TMP_DIR/terraform_refresh.stdout"
    REFRESH_EXIT=${PIPESTATUS[0]}
    >&2 cat "$STEP_TMP_DIR/terraform_refresh.stderr"

    set -e

    if [[ "$TERRAFORM_BACKEND_TYPE" == "cloud" || "$TERRAFORM_BACKEND_TYPE" == "remote" ]]; then
        if remote-run-id "$STEP_TMP_DIR/terraform_refresh.stdout" "$STEP_TMP_DIR/terraform_refresh.stderr" >"$STEP_TMP_DIR/remote-run-id.stdout" 2>"$STEP_TMP_DIR/remote-run-id.stderr"; then
            RUN_ID="$(<"$STEP_TMP_DIR/remote-run-id.stdout")"
            set_output run_id "$RUN_ID"
        else
            debug_log "Failed to get remote run-id"
            debug_file "$STEP_TMP_DIR/remote-run-id.stderr"
        fi
    fi

    if [[ $REFRESH_EXIT -eq 0 ]]; then
        echo "Refresh complete"
    else
        if lock-info "$STEP_TMP_DIR/terraform_refresh.stderr"; then
            set_output failure-reason state-locked
        else
            set_output failure-reason refresh-failed
        fi
        exit 1
    fi
}

refresh
