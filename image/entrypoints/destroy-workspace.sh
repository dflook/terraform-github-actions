#!/bin/bash

source /usr/local/actions.sh

debug
setup
init-backend
select-workspace
set-plan-args

(cd "$INPUT_PATH" \
 && terraform destroy -input=false -auto-approve -lock-timeout=300s $PLAN_ARGS \
 && terraform workspace select -no-color "default" \
 && terraform workspace delete -no-color -lock-timeout=300s "$workspace")
