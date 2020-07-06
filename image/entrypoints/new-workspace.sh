#!/bin/bash

source /usr/local/actions.sh

debug
setup
init-backend

if (cd "$INPUT_PATH" && terraform workspace list -no-color | workspace_exists "$workspace"); then
  echo "Workspace appears to exist, selecting it"
  (cd "$INPUT_PATH" && terraform workspace select -no-color "$workspace")
else
  (cd "$INPUT_PATH" && terraform workspace new -no-color -lock-timeout=300s "$workspace")
fi
