#!/bin/bash

source /usr/local/actions.sh

debug
setup
init

(cd "$INPUT_PATH" && terraform version -no-color | convert_version) >/tmp/version.txt

enable_workflow_commands
cat /tmp/version.txt
disable_workflow_commands
