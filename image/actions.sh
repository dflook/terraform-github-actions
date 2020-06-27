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
  debug_cmd pwd
  debug_cmd ls -la
  debug_cmd ls $HOME
  debug_cmd printenv
  debug_cmd cat "$GITHUB_EVENT_PATH"
  echo
}

function detect-terraform-version() {
  local TF_SWITCH_OUTPUT

  TF_SWITCH_OUTPUT=$(cd "$INPUT_PATH" && echo "" | tfswitch | grep -e Switched -e Reading | sed 's/^.*Switched/Switched/')
  if echo "$TF_SWITCH_OUTPUT" | grep Reading >/dev/null; then
    echo "$TF_SWITCH_OUTPUT"
  else
    echo "Reading latest terraform version"
    tfswitch "$(latest_terraform_version)"
  fi
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

function setup() {
  export TF_DATA_DIR="$HOME/.dflook-terraform-data-dir"
  export TF_PLUGIN_CACHE_DIR="$HOME/.terraform.d/plugin-cache"
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
  detect-tfmask
}

function relative_to() {
  local abspath
  local relpath

  absbase="$1"
  relpath="$1"
  realpath --no-symlinks --canonicalize-missing --relative-base="$absbase" "$relpath"
}

function init() {
  rm -rf "$TF_DATA_DIR"
  (cd "$INPUT_PATH" && terraform init -input=false -backend=false)
}

function init-backend() {
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

  # Set workspace from parameter, allowing it to be overridden by TF_WORKSPACE.
  # If TF_WORKSPACE is set we don't want terraform init to use the value, in the case we are running new_workspace.sh this would cause an error
  readonly workspace="${TF_WORKSPACE:-$INPUT_WORKSPACE}"
  export workspace
  unset TF_WORKSPACE

  rm -rf "$TF_DATA_DIR"
  (cd "$INPUT_PATH" && terraform init -input=false -lock-timeout=300s $INIT_ARGS)
}

function select-workspace() {
  (cd "$INPUT_PATH" && terraform workspace select "$workspace")
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

  export PLAN_ARGS
}

function output() {
  (cd "$INPUT_PATH" && terraform output -json | convert_output)
}

function update_status() {
    local status="$1"

    echo "$status"

    if ! STATUS="$status" github_pr_comment status 2>&1 | sed 's/^/::debug::/'; then
        echo "Unable to update status on PR"
    fi
}

function random_string() {
  python3 -c "import random; import string; print(''.join(random.choice(string.ascii_lowercase) for i in range(8)))"
}