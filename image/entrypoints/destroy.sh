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
    set_output failure-reason destroy-failed
    exit 1
fi
