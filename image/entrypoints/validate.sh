#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup

# You can't properly validate without initializing.
# You can't initialize without having valid terraform.
# How do you get a full validation report? You can't.

# terraform.workspace will be evaluated during a validate, but it is not initialized properly.
# Pass through the workspace input, even if it doesn't make sense for some backends.

init || true

if ! (cd "$INPUT_PATH" && TF_WORKSPACE="$INPUT_WORKSPACE" terraform validate -json | convert_validate_report "$INPUT_PATH"); then
    (cd "$INPUT_PATH" && TF_WORKSPACE="$INPUT_WORKSPACE" terraform validate)
else
    echo -e "\033[1;32mSuccess!\033[0m The configuration is valid"
fi
