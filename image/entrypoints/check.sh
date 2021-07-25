#!/bin/bash

source /usr/local/actions.sh

debug
setup
init-backend
select-workspace
set-plan-args

disable_workflow_commands

set +e
(cd $INPUT_PATH && terraform plan -input=false -detailed-exitcode -lock-timeout=300s $PLAN_ARGS) \
    | $TFMASK

readonly TF_EXIT=${PIPESTATUS[0]}
set -e

if [[ $TF_EXIT -eq 1 ]]; then
    echo "Error running terraform"
    exit 1

elif [[ $TF_EXIT -eq 2 ]]; then

    echo "Changes detected!"
    exit 1

fi
