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
  enable_workflow_commands
  echo "::debug::" "$@"
  disable_workflow_commands
}

##
# Send a string to the error log
#
function error_log() {
  enable_workflow_commands
  echo "::error::" "$@"
  disable_workflow_commands
}


##
# Run a command and send the output to the debug log
#
# This will be visible in the workflow log if ACTIONS_STEP_DEBUG workflow secret is set.
function debug_cmd() {
  local CMD_NAME
  CMD_NAME=$(echo "$@")
  enable_workflow_commands
  "$@" | while IFS= read -r line; do echo "::debug::${CMD_NAME}:${line}"; done;
  disable_workflow_commands
}

##
# Set an output value
#
function set_output() {
  local name
  local value

  name="$1"
  value="${*:2}"

  enable_workflow_commands
  echo "::set-output name=${name}::${value}"
  disable_workflow_commands
}

##
# Start a log group
#
# All output between this and the next end_group will be collapsed into an expandable group
function start_group() {
  enable_workflow_commands
  echo "::group::$1"
  disable_workflow_commands
}

##
# End a log group
#
function end_group() {
  enable_workflow_commands
  echo "::endgroup::"
  disable_workflow_commands
}

##
# Enable to processing of workflow commands
#
function enable_workflow_commands() {
  if [[ -z "$WORKFLOW_COMMAND_TOKEN" ]]; then
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
  if [[ -n "$WORKFLOW_COMMAND_TOKEN" ]]; then
    echo "Tried to disable workflow commands, but they are already disabled"
    exit 1
  fi

  WORKFLOW_COMMAND_TOKEN=$(generate_command_token)
  echo "::stop-commands::${WORKFLOW_COMMAND_TOKEN}"
}

function generate_command_token() {
  python3 -c "import random; import string; print(''.join(random.choice(string.ascii_lowercase) for i in range(8)))"
}

disable_workflow_commands
