#!/bin/bash

source /usr/local/actions.sh

debug
setup
init-backend

if (cd "$INPUT_PATH" && terraform workspace list -no-color | workspace_exists "$INPUT_WORKSPACE"); then
  echo "Workspace appears to exist, selecting it"
  (cd "$INPUT_PATH" && terraform workspace select -no-color "$INPUT_WORKSPACE")
else
  (cd "$INPUT_PATH" && terraform workspace new -no-color -lock-timeout=300s "$INPUT_WORKSPACE")
fi
