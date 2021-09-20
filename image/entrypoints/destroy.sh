#!/bin/bash

source /usr/local/actions.sh

debug
setup
init-backend
select-workspace
set-plan-args

if ! (cd "$INPUT_PATH" && terraform destroy -input=false -auto-approve -lock-timeout=300s $PLAN_ARGS); then
    set_output failure-reason destroy-failed
    exit 1
fi
