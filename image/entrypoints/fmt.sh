#!/bin/bash

source /usr/local/actions.sh

debug
setup

disable_workflow_commands

terraform fmt -recursive -no-color "$INPUT_PATH"
