#!/bin/bash

source /usr/local/actions.sh

debug
setup
init

enable_workflow_commands
(cd "$INPUT_PATH" && terraform version -no-color | convert_version)
disable_workflow_commands
