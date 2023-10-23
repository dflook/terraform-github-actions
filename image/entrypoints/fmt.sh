#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup

$TOOL_COMMAND_NAME fmt -recursive -no-color "$INPUT_PATH"
