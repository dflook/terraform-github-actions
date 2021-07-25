#!/bin/bash

set -eo pipefail

source /usr/local/workflow_commands.sh

function debug() {
  if [[ -n "$ACTIONS_STEP_DEBUG" ]]; then
    start_group "Environment (ACTIONS_STEP_DEBUG)"
    debug_cmd ls -la /root
    debug_cmd pwd
    debug_cmd ls -la
    debug_cmd ls -la "$HOME"
    debug_cmd printenv
    debug_cmd cat "$GITHUB_EVENT_PATH"
    end_group
  fi
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
  if [[ -n $TERRAFORM_PRE_RUN ]]; then
    start_group "Executing TERRAFORM_PRE_RUN"

    echo "Executing init commands specified in 'TERRAFORM_PRE_RUN' environment variable"
    printf "%s" "$TERRAFORM_PRE_RUN" > /.prerun.sh
    bash -xeo pipefail /.prerun.sh

    end_group
  fi
}

function setup() {
  if [[ "$INPUT_PATH" == "" ]]; then
    error_log "input 'path' not set"
    exit 1
  fi

  if [[ ! -d "$INPUT_PATH" ]]; then
    error_log "Path does not exist: \"$INPUT_PATH\""
    exit 1
  fi

  TERRAFORM_BIN_DIR="$HOME/.dflook-terraform-bin-dir"
  export TF_DATA_DIR="$HOME/.dflook-terraform-data-dir"
  export TF_PLUGIN_CACHE_DIR="$HOME/.terraform.d/plugin-cache"
  unset TF_WORKSPACE

  # tfswitch guesses the wrong home directory...
  start_group "Installing Terraform"
  if [[ ! -d $TERRAFORM_BIN_DIR ]]; then
    debug_log "Initializing tfswitch with image default version"
    cp --recursive /root/.terraform.versions.default "$TERRAFORM_BIN_DIR"
  fi

  ln -s "$TERRAFORM_BIN_DIR" /root/.terraform.versions

  debug_cmd ls -lad /root/.terraform.versions
  debug_cmd ls -lad "$TERRAFORM_BIN_DIR"
  debug_cmd ls -la "$TERRAFORM_BIN_DIR"

  mkdir -p "$TF_DATA_DIR" "$TF_PLUGIN_CACHE_DIR"

  detect-terraform-version

  debug_cmd ls -la "$TERRAFORM_BIN_DIR"
  end_group

  detect-tfmask

  execute_run_commands
}

function relative_to() {
  local absbase
  local relpath

  absbase="$1"
  relpath="$2"
  realpath --no-symlinks --canonicalize-missing --relative-to="$absbase" "$relpath"
}

function init() {
  start_group "Initializing Terraform"

  write_credentials

  rm -rf "$TF_DATA_DIR"
  (cd "$INPUT_PATH" && terraform init -input=false -backend=false)

  end_group
}

function init-backend() {
  start_group "Initializing Terraform"

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


  end_group
}

function select-workspace() {
  start_group "Selecting workspace"

  (cd "$INPUT_PATH" && terraform workspace select "$INPUT_WORKSPACE")

  end_group
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
  enable_workflow_commands
  (cd "$INPUT_PATH" && terraform output -json | convert_output)
  disable_workflow_commands
}

function update_status() {
  local status="$1"

  enable_workflow_commands
  if ! STATUS="$status" github_pr_comment status 2>&1 | sed 's/^/::debug::/'; then
    disable_workflow_commands
    echo "$status"
    echo "Unable to update status on PR"
  else
    disable_workflow_commands
  fi
}

function random_string() {
  python3 -c "import random; import string; print(''.join(random.choice(string.ascii_lowercase) for i in range(32)))"
}

function write_credentials() {
  format_tf_credentials >> "$HOME/.terraformrc"
  netrc-credential-actions >> "$HOME/.netrc"
  echo "$TERRAFORM_SSH_KEY" >> /.ssh/id_rsa
  chmod 600 /.ssh/id_rsa
  chmod 700 /.ssh
  debug_cmd git config --list
}
