#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup
init-backend-workspace
set-plan-args

exec 3>&1

PLAN_OUT="$STEP_TMP_DIR/plan.out"
PLAN_ARGS="$PLAN_ARGS -lock=false"
plan

if [[ $PLAN_EXIT -eq 1 ]]; then
    if grep -q "Saving a generated plan is currently not supported" "$STEP_TMP_DIR/terraform_plan.stderr"; then
        # This terraform module is using the remote backend, which is deficient.
        set-remote-plan-args
        PLAN_OUT=""
        PLAN_ARGS="$PLAN_ARGS -lock=false"
        plan
    fi
fi

if [[ $PLAN_EXIT -eq 1 ]]; then
    echo "Error running terraform"
    cat >&2 "$STEP_TMP_DIR/terraform_plan.stderr"
    exit 1

elif [[ $PLAN_EXIT -eq 2 ]]; then

    echo "Changes detected!"
    set_output failure-reason changes-to-apply
    exit 1

fi
