#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup
init-backend-workspace
set-plan-args

exec 3>&1

destroy

if [[ $DESTROY_EXIT -eq 1 ]]; then
    if grep -q "Run variables are currently not supported" "$STEP_TMP_DIR/terraform_destroy.stderr"; then
        set-remote-plan-args
        destroy
    fi
fi

if [[ $DESTROY_EXIT -eq 1 ]]; then
    cat >&2 "$STEP_TMP_DIR/terraform_destroy.stderr"
    if lock-info "$STEP_TMP_DIR/terraform_destroy.stderr"; then
        set_output failure-reason state-locked
    else
        set_output failure-reason destroy-failed
    fi
    exit 1
fi

if [[ "$TERRAFORM_BACKEND_TYPE" == "remote" || "$TERRAFORM_BACKEND_TYPE" == "cloud" ]]; then
    terraform-cloud-workspace delete "$INPUT_WORKSPACE"
else
    # We can't delete an active workspace, so re-initialize with a 'default' workspace (which may not exist)
    init-backend-default-workspace

    # shellcheck disable=SC2086
    debug_log $TOOL_COMMAND_NAME workspace delete $VARIABLE_ARGS -no-color -lock-timeout=300s "$INPUT_WORKSPACE"
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME workspace delete $VARIABLE_ARGS -no-color -lock-timeout=300s "$INPUT_WORKSPACE")
fi
