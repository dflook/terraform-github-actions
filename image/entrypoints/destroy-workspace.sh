#!/bin/bash

source /usr/local/actions.sh

debug
setup
init-backend
select-workspace
set-plan-args

(cd "$INPUT_PATH" \
 && terraform destroy -input=false -auto-approve -lock-timeout=300s $PLAN_ARGS)

# We can't delete an active workspace, so re-initialize with a 'default' workspace (which may not exist)
workspace=$INPUT_WORKSPACE
INPUT_WORKSPACE=default
init-backend

(cd "$INPUT_PATH" \
 && terraform workspace delete -no-color -lock-timeout=300s "$workspace")
