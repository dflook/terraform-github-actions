#!/bin/bash

source /usr/local/actions.sh

debug
setup
init

disble_workflow_commands

(cd "$INPUT_PATH" && terraform version -no-color | tee | convert_version)
