#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup
init-backend
select-workspace
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
    set_output failure-reason destroy-failed
    exit 1
fi

# We can't delete an active workspace, so re-initialize with a 'default' workspace (which may not exist)
workspace=$INPUT_WORKSPACE
INPUT_WORKSPACE=default
init-backend

(cd "$INPUT_PATH" && terraform workspace delete -no-color -lock-timeout=300s "$workspace")
