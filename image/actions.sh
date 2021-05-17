#!/bin/bash

set -eo pipefail

function debug_log() {
  echo "::debug::" "$@"
}

function debug_cmd() {
  local CMD_NAME
  CMD_NAME=$(echo "$@")
  "$@" | while IFS= read -r line; do echo "::debug::${CMD_NAME}:${line}"; done;
}

function debug() {
  debug_cmd ls -la /root
  debug_cmd pwd
  debug_cmd ls -la
  debug_cmd ls -la $HOME
  debug_cmd printenv
  debug_cmd cat "$GITHUB_EVENT_PATH"
  echo
}

function detect-terraform-version() {
  local TF_SWITCH_OUTPUT

  debug_cmd tfswitch --version

  TF_SWITCH_OUTPUT=$(cd "$INPUT_PATH" && echo "" | tfswitch | grep -e Switched -e Reading | sed 's/^.*Switched/Switched/')
  if echo "$TF_SWITCH_OUTPUT" | grep Reading >/dev/null; then
    echo "$TF_SWITCH_OUTPUT"
  else
    echo "Reading latest terraform version"
    tfswitch "$(latest_terraform_version)"
  fi

  debug_cmd ls -la "$(which terraform)"
}

function job_markdown_ref() {
  echo "[${GITHUB_WORKFLOW} #${GITHUB_RUN_NUMBER}](https://github.com/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID})"
}

function detect-tfmask() {
  TFMASK="tfmask"
  if ! hash tfmask 2>/dev/null; then
    TFMASK="cat"
  fi

  export TFMASK
}

function execute_run_commands() {
  if [[ -n $INPUT_RUN ]]; then
    echo "Executing init commands specified in 'run' parameter"
    eval "$INPUT_RUN"
  fi
  if [[ -n $TERRAFORM_PRE_RUN ]]
    echo "Executing init commands specified in 'TERRAFORM_PRE_RUN' environment variable"
    eval "$TERRAFORM_PRE_RUN"
  fi
}

function setup() {
  TERRAFORM_BIN_DIR="$HOME/.dflook-terraform-bin-dir"
  export TF_DATA_DIR="$HOME/.dflook-terraform-data-dir"
  export TF_PLUGIN_CACHE_DIR="$HOME/.terraform.d/plugin-cache"
  unset TF_WORKSPACE

  # tfswitch guesses the wrong home directory...
  if [[ ! -d $TERRAFORM_BIN_DIR ]]; then
    debug_log "Initializing tfswitch with image default version"
    cp --recursive /root/.terraform.versions.default $TERRAFORM_BIN_DIR
  fi

  ln -s $TERRAFORM_BIN_DIR /root/.terraform.versions

  debug_cmd ls -lad /root/.terraform.versions
  debug_cmd ls -lad $TERRAFORM_BIN_DIR
  debug_cmd ls -la $TERRAFORM_BIN_DIR

  mkdir -p "$TF_DATA_DIR" "$TF_PLUGIN_CACHE_DIR"

  if [[ "$INPUT_PATH" == "" ]]; then
    echo "::error:: input 'path' not set"
    exit 1
  fi

  if [[ ! -d "$INPUT_PATH" ]]; then
    echo "::error:: Path does not exist: \"$INPUT_PATH\""
    exit 1
  fi

  detect-terraform-version

  debug_cmd ls -la $TERRAFORM_BIN_DIR

  detect-tfmask

  execute_run_commands
}

function relative_to() {
  local abspath
  local relpath

  absbase="$1"
  relpath="$2"
  realpath --no-symlinks --canonicalize-missing --relative-to="$absbase" "$relpath"
}

function init() {
  write_credentials

  rm -rf "$TF_DATA_DIR"
  (cd "$INPUT_PATH" && terraform init -input=false -backend=false)
}

function init-backend() {
  write_credentials

  INIT_ARGS=""

  if [[ -n "$INPUT_BACKEND_CONFIG_FILE" ]]; then
      for file in $(echo "$INPUT_BACKEND_CONFIG_FILE" | tr ',' '\n'); do
          INIT_ARGS="$INIT_ARGS -backend-config=$(relative_to "$INPUT_PATH" "$file")"
      done
  fi

  if [[ -n "$INPUT_BACKEND_CONFIG" ]]; then
      for config in $(echo "$INPUT_BACKEND_CONFIG" | tr ',' '\n'); do
          INIT_ARGS="$INIT_ARGS -backend-config=$config"
      done
  fi

  export INIT_ARGS

  rm -rf "$TF_DATA_DIR"

  set +e
  (cd "$INPUT_PATH" && TF_WORKSPACE=$INPUT_WORKSPACE terraform init -input=false $INIT_ARGS \
      2>"$PLAN_DIR/init_error.txt")

  local INIT_EXIT=$?
  set -e

  if [[ $INIT_EXIT -eq 0 ]]; then
    cat "$PLAN_DIR/init_error.txt" >&2
  else
    if grep -q "No existing workspaces." "$PLAN_DIR/init_error.txt" || grep -q "Failed to select workspace" "$PLAN_DIR/init_error.txt"; then
      # Couldn't select workspace, but we don't really care.
      # select-workspace will give a better error if the workspace is required to exist
      :
    else
      cat "$PLAN_DIR/init_error.txt" >&2
      exit $INIT_EXIT
    fi
  fi
}

function select-workspace() {
  (cd "$INPUT_PATH" && terraform workspace select "$INPUT_WORKSPACE")
}

function set-plan-args() {
  PLAN_ARGS=""

  if [[ "$INPUT_PARALLELISM" -ne 0 ]]; then
      PLAN_ARGS="$PLAN_ARGS -parallelism=$INPUT_PARALLELISM"
  fi

  if [[ -n "$INPUT_VAR" ]]; then
      for var in $(echo "$INPUT_VAR" | tr ',' '\n'); do
          PLAN_ARGS="$PLAN_ARGS -var $var"
      done
  fi

  if [[ -n "$INPUT_VAR_FILE" ]]; then
      for file in $(echo "$INPUT_VAR_FILE" | tr ',' '\n'); do
          PLAN_ARGS="$PLAN_ARGS -var-file=$(relative_to "$INPUT_PATH" "$file")"
      done
  fi

  if [[ -n "$INPUT_VARIABLES" ]]; then
    echo "$INPUT_VARIABLES" > /.terraform-variables.tfvars
    PLAN_ARGS="$PLAN_ARGS -var-file=/.terraform-variables.tfvars"
  fi

  export PLAN_ARGS
}

function output() {
  (cd "$INPUT_PATH" && terraform output -json | convert_output)
}

function update_status() {
    local status="$1"

    if ! STATUS="$status" github_pr_comment status 2>&1 | sed 's/^/::debug::/'; then
        echo "$status"
        echo "Unable to update status on PR"
    fi
}

function random_string() {
  python3 -c "import random; import string; print(''.join(random.choice(string.ascii_lowercase) for i in range(8)))"
}

function write_credentials() {
  format_tf_credentials >> $HOME/.terraformrc

  echo "$TERRAFORM_SSH_KEY" >> /.ssh/id_rsa
  chmod 600 /.ssh/id_rsa
  chmod 700 /.ssh
}
