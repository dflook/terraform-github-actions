#!/bin/bash

##
# GitHub Actions workflow commands
#
# The processing of workflow commands is disabled, with these functions becoming the only way to
# use them. Processing can be enabled again using enable_workflow_commands

##
# Send a string to the debug log
#
# This will be visible in the workflow log if ACTIONS_STEP_DEBUG workflow secret is set.
function debug_log() {
    echo "::debug::" "$@"
}

##
# Send a string to the error log
#
function error_log() {
    echo "::error::" "$@"
}

##
# Run a command and send the output to the debug log
#
# This will be visible in the workflow log if ACTIONS_STEP_DEBUG workflow secret is set.
function debug_cmd() {
    local CMD_NAME
    CMD_NAME="$*"
    "$@" | while IFS= read -r line; do echo "::debug::${CMD_NAME}:${line}"; done
}

##
# Print a file to the debug log
#
# This will be visible in the workflow log if ACTIONS_STEP_DEBUG workflow secret is set.
function debug_file() {
    local FILE_PATH
    FILE_PATH="$1"

    if [[ -s "$FILE_PATH" ]]; then
        # File exists, and is not empty
        sed "s|^|::debug::$FILE_PATH:|" "$FILE_PATH"
    elif [[ -f "$FILE_PATH" ]]; then
        # file exists but is empty
        echo "::debug::$FILE_PATH is empty"
    else
        echo "::debug::$FILE_PATH does not exist"
    fi
}

##
# Set an output value
#
function set_output() {
    local name
    local value

    name="$1"
    value="${*:2}"

    if [[ -v GITHUB_OUTPUT && -f "$GITHUB_OUTPUT" ]]; then
      echo "${name}=${value}" >> "$GITHUB_OUTPUT"
    else
      echo "::set-output name=${name}::${value}"
    fi
}

##
# Start a log group
#
# All output between this and the next end_group will be collapsed into an expandable group
function start_group() {
    echo "::group::$1"
}

##
# End a log group
#
function end_group() {
    echo "::endgroup::"
}

##
# Enable to processing of workflow commands
#
function enable_workflow_commands() {
    if [[ ! -v WORKFLOW_COMMAND_TOKEN ]]; then
        echo "Tried to enable workflow commands, but they are already enabled"
        exit 1
    fi

    echo "::${WORKFLOW_COMMAND_TOKEN}::"
    unset WORKFLOW_COMMAND_TOKEN
}

##
# Disable the processing of workflow commands
#
function disable_workflow_commands() {
    if [[ -v WORKFLOW_COMMAND_TOKEN ]]; then
        echo "Tried to disable workflow commands, but they are already disabled"
        exit 1
    fi

    WORKFLOW_COMMAND_TOKEN=$(generate_command_token)
    echo "::stop-commands::${WORKFLOW_COMMAND_TOKEN}"
}

function generate_command_token() {
    python3 -c "import random; import string; print(''.join(random.choice(string.ascii_lowercase) for i in range(64)))"
}
