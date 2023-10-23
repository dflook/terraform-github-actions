#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup
init

debug_cmd $TOOL_COMMAND_NAME version -json
(cd "$INPUT_PATH" && $TOOL_COMMAND_NAME version -json | convert_version)
