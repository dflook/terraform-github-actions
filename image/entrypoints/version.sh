#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup
init

debug_cmd terraform version -json
(cd "$INPUT_PATH" && terraform version -json | convert_version)
