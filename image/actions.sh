#!/bin/bash

set -euo pipefail

function repair_environment() {
    if [[ ! -f "$GITHUB_EVENT_PATH" || ! -d "$HOME" ]]; then
        echo "Currently using an actions runner with a broken environment."
    fi

    if [[ ! -f "$GITHUB_EVENT_PATH" ]] && find / -name event.json -quit; then
        # GITHUB_EVENT_PATH is missing, but we can find it
        GITHUB_EVENT_PATH=$(find / -name event.json -print -quit)
        export GITHUB_EVENT_PATH
        echo "Repaired GITHUB_EVENT_PATH=$GITHUB_EVENT_PATH"
    fi

    if [[ ! -d "$HOME" ]]; then
        # HOME doesn't exist... is it near GITHUB_EVENT_PATH?

        local ACTUAL_HOME
        ACTUAL_HOME=$(realpath "$(dirname "$GITHUB_EVENT_PATH")/../_github_home")

        if [[ -d "$ACTUAL_HOME" ]]; then
          HOME="$ACTUAL_HOME"
          export HOME
          echo "Repaired HOME=$HOME"
        fi
    fi
}
repair_environment

# shellcheck source=../workflow_commands.sh
source /usr/local/workflow_commands.sh

function debug() {
    debug_cmd pwd
    debug_cmd printenv
    debug_tree "$HOME"
    debug_file "$GITHUB_EVENT_PATH"
    echo
}

function detect-terraform-version() {
    TERRAFORM_BIN_CACHE_DIR="/var/terraform:$JOB_TMP_DIR/terraform-bin-dir" TERRAFORM_BIN_CHECKSUM_DIR="/var/terraform" terraform-version
    debug_cmd ls -la "$(command -v terraform)"

    local TF_VERSION
    TF_VERSION=$(terraform version -json | jq -r '.terraform_version' 2>/dev/null || terraform version | grep 'Terraform v' | sed 's/Terraform v//')

    TERRAFORM_VER_MAJOR=$(echo "$TF_VERSION" | cut -d. -f1)
    TERRAFORM_VER_MINOR=$(echo "$TF_VERSION" | cut -d. -f2)
    TERRAFORM_VER_PATCH=$(echo "$TF_VERSION" | cut -d. -f3)

    terraform version > "$STEP_TMP_DIR/terraform_version.stdout"
    cat "$STEP_TMP_DIR/terraform_version.stdout"

    if grep --quiet OpenTofu "$STEP_TMP_DIR/terraform_version.stdout"; then
        export TOOL_PRODUCT_NAME="OpenTofu"
        export TOOL_COMMAND_NAME="tofu"
    else
        export TOOL_PRODUCT_NAME="Terraform"
        export TOOL_COMMAND_NAME="terraform"
    fi

    debug_log "$TOOL_PRODUCT_NAME version major $TERRAFORM_VER_MAJOR minor $TERRAFORM_VER_MINOR patch $TERRAFORM_VER_PATCH"
}

function test-terraform-version() {
    local OP="$1"
    local VER="$2"

    python3 -c "exit(0 if ($TERRAFORM_VER_MAJOR, $TERRAFORM_VER_MINOR, $TERRAFORM_VER_PATCH) $OP tuple(int(v) for v in '$VER'.split('.')) else 1)"
}

function job_markdown_ref() {
    echo "[${GITHUB_WORKFLOW} #${GITHUB_RUN_NUMBER}](${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID})"
}

function detect-tfmask() {
    TFMASK="tfmask"
    if ! hash tfmask 2>/dev/null; then
        TFMASK="cat"
    fi

    export TFMASK
}

function execute_run_commands() {
    if [[ -v TERRAFORM_PRE_RUN ]]; then
        start_group "Executing TERRAFORM_PRE_RUN"

        echo "Executing init commands specified in 'TERRAFORM_PRE_RUN' environment variable"
        printf "%s" "$TERRAFORM_PRE_RUN" >"$STEP_TMP_DIR/TERRAFORM_PRE_RUN.sh"
        disable_workflow_commands
        bash -xeo pipefail "$STEP_TMP_DIR/TERRAFORM_PRE_RUN.sh"
        enable_workflow_commands

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

    if [[ ! -v TERRAFORM_ACTIONS_GITHUB_TOKEN ]]; then
      if [[ -v GITHUB_TOKEN ]]; then
        export TERRAFORM_ACTIONS_GITHUB_TOKEN="$GITHUB_TOKEN"
      fi
    fi

    if [[ -v OPENTOFU_VERSION ]]; then
        export OPENTOFU=true
    fi

    if ! github_comment_react +1 2>"$STEP_TMP_DIR/github_comment_react.stderr"; then
        debug_file "$STEP_TMP_DIR/github_comment_react.stderr"
    fi

    export TF_DATA_DIR="$STEP_TMP_DIR/terraform-data-dir"
    export TF_PLUGIN_CACHE_DIR="$HOME/.terraform.d/plugin-cache"
    mkdir -p "$TF_DATA_DIR" "$TF_PLUGIN_CACHE_DIR" "$JOB_TMP_DIR/terraform-bin-dir"

    unset TF_WORKSPACE

    write_credentials

    if [[ -v OPENTOFU ]]; then
        start_group "Installing OpenTofu"
    else
        start_group "Installing Terraform"
    fi

    detect-terraform-version

    TERRAFORM_BACKEND_TYPE=$(terraform-backend)
    readonly TERRAFORM_BACKEND_TYPE
    if [[ "$TERRAFORM_BACKEND_TYPE" != "" ]]; then
        echo "Detected $TERRAFORM_BACKEND_TYPE backend"
    fi
    export TERRAFORM_BACKEND_TYPE

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

##
# Initialize terraform without a backend
#
# This only validates and installs plugins
function init() {
    start_group "Initializing $TOOL_PRODUCT_NAME"

    rm -rf "$TF_DATA_DIR"
    debug_log "$TOOL_COMMAND_NAME" init -input=false -backend=false
    (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME init -input=false -backend=false)

    end_group
}

##
# Initialize terraform for running tests
#
# This installs modules and providers for the module and all tests
function init-test() {
    start_group "Initializing $TOOL_PRODUCT_NAME"

    rm -rf "$TF_DATA_DIR"

    if [[ -n "$INPUT_TEST_DIRECTORY" ]]; then
        debug_log "$TOOL_COMMAND_NAME" init -input=false -backend=false -test-directory "$INPUT_TEST_DIRECTORY"
        (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME init -input=false -backend=false -test-directory "$INPUT_TEST_DIRECTORY")
    else
        debug_log "$TOOL_COMMAND_NAME" init -input=false -backend=false
        (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME init -input=false -backend=false)
    fi

    end_group
}

function set-init-args() {
    INIT_ARGS=""

    if [[ -n "$INPUT_BACKEND_CONFIG_FILE" ]]; then
        for file in $(echo "$INPUT_BACKEND_CONFIG_FILE" | tr ',' '\n'); do

            if [[ ! -f "$file" ]]; then
                error_log "Path does not exist: \"$file\""
                exit 1
            fi

            INIT_ARGS="$INIT_ARGS -backend-config=$(relative_to "$INPUT_PATH" "$file")"
        done
    fi

    if [[ -n "$INPUT_BACKEND_CONFIG" ]]; then
        for config in $(echo "$INPUT_BACKEND_CONFIG" | tr ',' '\n'); do
            INIT_ARGS="$INIT_ARGS -backend-config=$config"
        done
    fi

    export INIT_ARGS
}

##
# Initialize the backend for a specific workspace
#
# The workspace must already exist, or the job will be failed
function init-backend-workspace() {
    start_group "Initializing $TOOL_PRODUCT_NAME"

    set-init-args

    rm -rf "$TF_DATA_DIR"

    # shellcheck disable=SC2016
    debug_log TF_WORKSPACE="$INPUT_WORKSPACE" "$TOOL_COMMAND_NAME" init -input=false '$INIT_ARGS'  # don't expand INIT_ARGS

    set +e
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && TF_WORKSPACE=$INPUT_WORKSPACE $TOOL_COMMAND_NAME init -input=false $INIT_ARGS \
        2>"$STEP_TMP_DIR/terraform_init.stderr")

    local INIT_EXIT=$?
    set -e

    if [[ $INIT_EXIT -eq 0 ]]; then
        cat "$STEP_TMP_DIR/terraform_init.stderr" >&2
    else
        if grep -q "No existing workspaces." "$STEP_TMP_DIR/terraform_init.stderr" || grep -q "Failed to select workspace" "$STEP_TMP_DIR/terraform_init.stderr" || grep -q "Currently selected workspace.*does not exist" "$STEP_TMP_DIR/terraform_init.stderr"; then
            # Couldn't select workspace, but we don't really care.
            # select-workspace will give a better error if the workspace is required to exist
            cat "$STEP_TMP_DIR/terraform_init.stderr"
        else
            cat "$STEP_TMP_DIR/terraform_init.stderr" >&2
            exit $INIT_EXIT
        fi
    fi

    end_group

    select-workspace
}

##
# Initialize terraform to use the default workspace
#
# This can be used to initialize when you don't know if a given workspace exists
# This can NOT be used with remote backend, as they have no default workspace
function init-backend-default-workspace() {
    start_group "Initializing $TOOL_PRODUCT_NAME"

    set-init-args

    rm -rf "$TF_DATA_DIR"

    # shellcheck disable=SC2016
    debug_log "$TOOL_COMMAND_NAME" init -input=false '$INIT_ARGS'  # don't expand INIT_ARGS
    set +e
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME init -input=false $INIT_ARGS \
        2>"$STEP_TMP_DIR/terraform_init.stderr")

    local INIT_EXIT=$?
    set -e

    if [[ $INIT_EXIT -eq 0 ]]; then
        cat "$STEP_TMP_DIR/terraform_init.stderr" >&2
    else
        if grep -q "No existing workspaces." "$STEP_TMP_DIR/terraform_init.stderr" || grep -q "Failed to select workspace" "$STEP_TMP_DIR/terraform_init.stderr" || grep -q "Currently selected workspace.*does not exist" "$STEP_TMP_DIR/terraform_init.stderr"; then
            # Couldn't select workspace, but we don't really care.
            # select-workspace will give a better error if the workspace is required to exist
            cat "$STEP_TMP_DIR/terraform_init.stderr"
        else
            cat "$STEP_TMP_DIR/terraform_init.stderr" >&2
            exit $INIT_EXIT
        fi
    fi

    end_group
}

function select-workspace() {
    local WORKSPACE_EXIT

    debug_log "$TOOL_COMMAND_NAME" workspace select "$INPUT_WORKSPACE"
    set +e
    (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME workspace select "$INPUT_WORKSPACE") >"$STEP_TMP_DIR/workspace_select" 2>&1
    WORKSPACE_EXIT=$?
    set -e

    if [[ -s "$STEP_TMP_DIR/workspace_select" ]]; then
        start_group "Selecting workspace"

        if [[ $WORKSPACE_EXIT -ne 0 ]] && grep -q "workspaces not supported" "$STEP_TMP_DIR/workspace_select" && [[ $INPUT_WORKSPACE == "default" ]]; then
            echo "The full name of a remote workspace is set by the terraform configuration, selecting a different one is not supported"
            WORKSPACE_EXIT=0
        elif [[ $WORKSPACE_EXIT -ne 0 && "$TERRAFORM_BACKEND_TYPE" == "cloud" ]]; then
            # workspace select doesn't work with partial cloud config, we'll just have to try it and see
            echo "Using the $INPUT_WORKSPACE workspace"
            export TF_WORKSPACE="$INPUT_WORKSPACE"
            WORKSPACE_EXIT=0
        else
            cat "$STEP_TMP_DIR/workspace_select"
        fi

        end_group
    fi

    if [[ $WORKSPACE_EXIT -ne 0 ]]; then
        exit $WORKSPACE_EXIT
    fi
}

function set-common-plan-args() {
    PLAN_ARGS=""
    PARALLEL_ARG=""

    if [[ "$INPUT_PARALLELISM" -ne 0 ]]; then
        PARALLEL_ARG="-parallelism=$INPUT_PARALLELISM"
    fi

    if [[ -v INPUT_TARGET ]]; then
        if [[ -n "$INPUT_TARGET" ]]; then
            for target in $(echo "$INPUT_TARGET" | tr ',' '\n'); do
                PLAN_ARGS="$PLAN_ARGS -target $target"
            done
        fi
    fi

    if [[ -v INPUT_REPLACE ]]; then
        if [[ -n "$INPUT_REPLACE" ]]; then
            for target in $(echo "$INPUT_REPLACE" | tr ',' '\n'); do
                PLAN_ARGS="$PLAN_ARGS -replace $target"
            done
        fi
    fi

    if [[ -v INPUT_DESTROY ]]; then
        if [[ "$INPUT_DESTROY" == "true" ]]; then
            PLAN_ARGS="$PLAN_ARGS -destroy"
        fi
    fi

    if [[ -v INPUT_REFRESH ]]; then
        if [[ "$INPUT_REFRESH" == "false" ]]; then
          PLAN_ARGS="$PLAN_ARGS -refresh=false"
        fi
    fi
}

function set-variable-args() {
    VARIABLE_ARGS=""

    if [[ -n "$INPUT_VAR_FILE" ]]; then
        for file in $(echo "$INPUT_VAR_FILE" | tr ',' '\n'); do

            if [[ ! -f "$file" ]]; then
                error_log "Path does not exist: \"$file\""
                exit 1
            fi

            VARIABLE_ARGS="$VARIABLE_ARGS -var-file=$(relative_to "$INPUT_PATH" "$file")"
        done
    fi

    if [[ -n "$INPUT_VARIABLES" ]]; then
        echo "$INPUT_VARIABLES" >"$STEP_TMP_DIR/variables.tfvars"
        VARIABLE_ARGS="$VARIABLE_ARGS -var-file=$STEP_TMP_DIR/variables.tfvars"
    fi
}

function set-deprecated-var-args() {
    DEPRECATED_VAR_ARGS=""

    if [[ -n "$INPUT_VAR" ]]; then
        for var in $(echo "$INPUT_VAR" | tr ',' '\n'); do
            DEPRECATED_VAR_ARGS="$DEPRECATED_VAR_ARGS -var $var"
        done
    fi
}

function masked-deprecated-vars() {
  if [[ -n "$DEPRECATED_VAR_ARGS" ]]; then
    echo "-var <masked>"
  else
    echo ""
  fi
}

function set-plan-args() {
    set-common-plan-args
    set-deprecated-var-args
    set-variable-args

    export PLAN_ARGS
}

function set-remote-plan-args() {
    set-common-plan-args
    VARIABLE_ARGS=""
    DEPRECATED_VAR_ARGS=""

    local AUTO_TFVARS_COUNTER=0

    if [[ -n "$INPUT_VAR_FILE" ]]; then
        for file in $(echo "$INPUT_VAR_FILE" | tr ',' '\n'); do
            cp "$file" "$INPUT_PATH/zzzz-dflook-terraform-github-actions-$AUTO_TFVARS_COUNTER.auto.tfvars"
            AUTO_TFVARS_COUNTER=$((AUTO_TFVARS_COUNTER + 1))
        done
    fi

    if [[ -n "$INPUT_VARIABLES" ]]; then
        echo "$INPUT_VARIABLES" >"$STEP_TMP_DIR/variables.tfvars"
        cp "$STEP_TMP_DIR/variables.tfvars" "$INPUT_PATH/zzzz-dflook-terraform-github-actions-$AUTO_TFVARS_COUNTER.auto.tfvars"
    fi

    export PLAN_ARGS
}

function output() {
    debug_log "$TOOL_COMMAND_NAME" output -json
    (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME output -json | tee "$STEP_TMP_DIR/terraform_output.json" | convert_output)
}

function random_string() {
    python3 -c "import random; import string; print(''.join(random.choice(string.ascii_lowercase) for i in range(8)))"
}

function write_credentials() {
    CREDS_DIR="$STEP_TMP_DIR/credentials"
    mkdir -p "$CREDS_DIR"

    if [[ -f "$HOME/.terraformrc" ]]; then
        debug_log "Backing up $HOME/.terraformrc"
        cp "$HOME/.terraformrc" "$CREDS_DIR/.terraformrc"
        mv "$HOME/.terraformrc" "$HOME/.dflook-terraformrc-backup"
    else
        touch "$CREDS_DIR/.terraformrc"
    fi
    ln -s "$CREDS_DIR/.terraformrc" "$HOME/.terraformrc"

    format_tf_credentials >>"$CREDS_DIR/.terraformrc"
    chown --reference "$HOME" "$CREDS_DIR/.terraformrc"

    if [[ -f "$HOME/.netrc" ]]; then
        debug_log "Backing up $HOME/.netrc"
        cp "$HOME/.netrc" "$CREDS_DIR/.netrc"
        mv "$HOME/.netrc" "$HOME/.dflook-netrc-backup"
    else
        touch "$CREDS_DIR/.netrc"
    fi
    ln -s "$CREDS_DIR/.netrc" "$HOME/.netrc"

    netrc-credential-actions >>"$CREDS_DIR/.netrc"
    chown --reference "$HOME" "$CREDS_DIR/.netrc"

    chmod 700 /.ssh
    if [[ -v TERRAFORM_SSH_KEY ]]; then
        echo "$TERRAFORM_SSH_KEY" >>/.ssh/id_rsa
        chmod 600 /.ssh/id_rsa
    fi
}

function plan() {

    local PLAN_OUT_ARG
    if [[ -n "$PLAN_OUT" ]]; then
        PLAN_OUT_ARG="-out=$PLAN_OUT"
    else
        PLAN_OUT_ARG=""
    fi

    # shellcheck disable=SC2086
    debug_log $TOOL_COMMAND_NAME plan -input=false -no-color -detailed-exitcode -lock-timeout=300s $PARALLEL_ARG $PLAN_OUT_ARG $PLAN_ARGS "$(masked-deprecated-vars)" $VARIABLE_ARGS

    set +e
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME plan -input=false -no-color -detailed-exitcode -lock-timeout=300s $PARALLEL_ARG $PLAN_OUT_ARG $PLAN_ARGS $DEPRECATED_VAR_ARGS $VARIABLE_ARGS ) \
        2>"$STEP_TMP_DIR/terraform_plan.stderr" \
        | $TFMASK \
        | tee /dev/fd/3 "$STEP_TMP_DIR/terraform_plan.stdout" \
        | compact_plan \
            >"$STEP_TMP_DIR/plan.txt"

    # shellcheck disable=SC2034
    PLAN_EXIT=${PIPESTATUS[0]}
    set -e

    if [[ "$TERRAFORM_BACKEND_TYPE" == "remote" || "$TERRAFORM_BACKEND_TYPE" == "cloud" ]]; then
        if remote-run-id "$STEP_TMP_DIR/terraform_plan.stdout" >"$STEP_TMP_DIR/remote-run-id.stdout" 2>"$STEP_TMP_DIR/remote-run-id.stderr"; then
            RUN_ID="$(<"$STEP_TMP_DIR/remote-run-id.stdout")"
            set_output run_id "$RUN_ID"
        else
            debug_log "Failed to get remote run-id"
            debug_file "$STEP_TMP_DIR/remote-run-id.stderr"
        fi
    fi
}

function destroy() {
    # shellcheck disable=SC2086
    debug_log $TOOL_COMMAND_NAME destroy -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG $PLAN_ARGS "$(masked-deprecated-vars)" $VARIABLE_ARGS

    set +e
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME destroy -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG $PLAN_ARGS $DEPRECATED_VAR_ARGS $VARIABLE_ARGS) \
        2>"$STEP_TMP_DIR/terraform_destroy.stderr" \
        | tee /dev/fd/3 \
            >"$STEP_TMP_DIR/terraform_destroy.stdout"

    # shellcheck disable=SC2034
    DESTROY_EXIT=${PIPESTATUS[0]}
    set -e
}

function force_unlock() {
    echo "Unlocking state with ID: $INPUT_LOCK_ID"
    debug_log "$TOOL_COMMAND_NAME" force-unlock -force "$INPUT_LOCK_ID"
    (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME force-unlock -force "$INPUT_LOCK_ID")
}

# Every file written to disk should use one of these directories
STEP_TMP_DIR="/tmp"
JOB_TMP_DIR="$HOME/.dflook-terraform-github-actions"
WORKSPACE_TMP_DIR=".dflook-terraform-github-actions/$(random_string)"
readonly STEP_TMP_DIR JOB_TMP_DIR WORKSPACE_TMP_DIR
export STEP_TMP_DIR JOB_TMP_DIR WORKSPACE_TMP_DIR

function fix_owners() {
    if [[ -d "$GITHUB_WORKSPACE/.dflook-terraform-github-actions" ]]; then
        chown -R --reference "$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/.dflook-terraform-github-actions" || true
        debug_tree "$GITHUB_WORKSPACE/.dflook-terraform-github-actions"
    fi

    if [[ -d "$HOME/.dflook-terraform-github-actions" ]]; then
        chown -R --reference "$HOME" "$HOME/.dflook-terraform-github-actions" || true
    fi
    if [[ -d "$HOME/.terraform.d" ]]; then
        chown -R --reference "$HOME" "$HOME/.terraform.d" || true
    fi

    if [[ -d "$INPUT_PATH" ]]; then
        debug_cmd find "$INPUT_PATH" -regex '.*/zzzz-dflook-terraform-github-actions-[0-9]+\.auto\.tfvars' -print -delete || true
    fi

    if [[ -f "$HOME/.terraformrc" ]]; then
        rm -f "$HOME/.terraformrc"
    fi
    if [[ -f "$HOME/.dflook-terraformrc-backup" ]]; then
        debug_log "Restoring $HOME/.terraformrc"
        mv "$HOME/.dflook-terraformrc-backup" "$HOME/.terraformrc"
    fi

    if [[ -f "$HOME/.netrc" ]]; then
        rm -f "$HOME/.netrc"
    fi
    if [[ -f "$HOME/.dflook-netrc-backup" ]]; then
        debug_log "Restoring $HOME/.netrc"
        mv "$HOME/.dflook-netrc-backup" "$HOME/.netrc"
    fi

    debug_tree "$HOME"
}

trap fix_owners EXIT
