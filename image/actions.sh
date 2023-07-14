#!/bin/bash

set -euo pipefail

# shellcheck source=../workflow_commands.sh
source /usr/local/workflow_commands.sh

function debug() {
    debug_cmd ls -la /root
    debug_cmd pwd
    debug_cmd ls -la
    debug_cmd ls -la "$HOME"
    debug_cmd printenv
    debug_file "$GITHUB_EVENT_PATH"
    echo
}

function detect-terraform-version() {
    debug_cmd ls -la "/usr/local/bin"
    debug_cmd ls -la "$JOB_TMP_DIR/terraform-bin-dir"
    TERRAFORM_BIN_CACHE_DIR="/var/terraform:$JOB_TMP_DIR/terraform-bin-dir" TERRAFORM_BIN_CHECKSUM_DIR="/var/terraform" terraform-version
    debug_cmd ls -la "$(which terraform)"

    local TF_VERSION
    TF_VERSION=$(terraform version -json | jq -r '.terraform_version' 2>/dev/null || terraform version | grep 'Terraform v' | sed 's/Terraform v//')

    TERRAFORM_VER_MAJOR=$(echo "$TF_VERSION" | cut -d. -f1)
    TERRAFORM_VER_MINOR=$(echo "$TF_VERSION" | cut -d. -f2)
    TERRAFORM_VER_PATCH=$(echo "$TF_VERSION" | cut -d. -f3)

    debug_log "Terraform version major $TERRAFORM_VER_MAJOR minor $TERRAFORM_VER_MINOR patch $TERRAFORM_VER_PATCH"
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

    if ! github_comment_react +1 2>"$STEP_TMP_DIR/github_comment_react.stderr"; then
        debug_file "$STEP_TMP_DIR/github_comment_react.stderr"
    fi

    export TF_DATA_DIR="$STEP_TMP_DIR/terraform-data-dir"
    export TF_PLUGIN_CACHE_DIR="$HOME/.terraform.d/plugin-cache"
    mkdir -p "$TF_DATA_DIR" "$TF_PLUGIN_CACHE_DIR" "$JOB_TMP_DIR/terraform-bin-dir"

    unset TF_WORKSPACE

    write_credentials

    start_group "Installing Terraform"

    detect-terraform-version

    readonly TERRAFORM_BACKEND_TYPE=$(terraform-backend)
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
    start_group "Initializing Terraform"

    rm -rf "$TF_DATA_DIR"
    debug_log terraform init -input=false -backend=false
    (cd "$INPUT_PATH" && terraform init -input=false -backend=false)

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
    start_group "Initializing Terraform"

    set-init-args

    rm -rf "$TF_DATA_DIR"

    debug_log TF_WORKSPACE=$INPUT_WORKSPACE terraform init -input=false '$INIT_ARGS'  # don't expand INIT_ARGS

    set +e
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && TF_WORKSPACE=$INPUT_WORKSPACE terraform init -input=false $INIT_ARGS \
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
    start_group "Initializing Terraform"

    set-init-args

    rm -rf "$TF_DATA_DIR"

    debug_log terraform init -input=false '$INIT_ARGS'  # don't expand INIT_ARGS
    set +e
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && terraform init -input=false $INIT_ARGS \
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

    debug_log terraform workspace select "$INPUT_WORKSPACE"
    set +e
    (cd "$INPUT_PATH" && terraform workspace select "$INPUT_WORKSPACE") >"$STEP_TMP_DIR/workspace_select" 2>&1
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
}

function set-plan-args() {
    set-common-plan-args

    if [[ -n "$INPUT_VAR" ]]; then
        for var in $(echo "$INPUT_VAR" | tr ',' '\n'); do
            PLAN_ARGS="$PLAN_ARGS -var $var"
        done
    fi

    if [[ -n "$INPUT_VAR_FILE" ]]; then
        for file in $(echo "$INPUT_VAR_FILE" | tr ',' '\n'); do

            if [[ ! -f "$file" ]]; then
                error_log "Path does not exist: \"$file\""
                exit 1
            fi

            PLAN_ARGS="$PLAN_ARGS -var-file=$(relative_to "$INPUT_PATH" "$file")"
        done
    fi

    if [[ -n "$INPUT_VARIABLES" ]]; then
        echo "$INPUT_VARIABLES" >"$STEP_TMP_DIR/variables.tfvars"
        PLAN_ARGS="$PLAN_ARGS -var-file=$STEP_TMP_DIR/variables.tfvars"
    fi

    export PLAN_ARGS
}

function set-remote-plan-args() {
    set-common-plan-args

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

    debug_cmd ls -la "$INPUT_PATH"

    export PLAN_ARGS
}

function output() {
    debug_log terraform output -json
    (cd "$INPUT_PATH" && terraform output -json | convert_output)
}

function update_status() {
    local status="$1"

    if ! STATUS="$status" github_pr_comment status 2>"$STEP_TMP_DIR/github_pr_comment.stderr"; then
        debug_file "$STEP_TMP_DIR/github_pr_comment.stderr"
    else
        debug_file "$STEP_TMP_DIR/github_pr_comment.stderr"
    fi
}

function random_string() {
    python3 -c "import random; import string; print(''.join(random.choice(string.ascii_lowercase) for i in range(8)))"
}

function write_credentials() {
    format_tf_credentials >>"$HOME/.terraformrc"
    chown --reference "$HOME" "$HOME/.terraformrc"
    netrc-credential-actions >>"$HOME/.netrc"
    chown --reference "$HOME" "$HOME/.netrc"

    chmod 700 /.ssh
    if [[ -v TERRAFORM_SSH_KEY ]]; then
        echo "$TERRAFORM_SSH_KEY" >>/.ssh/id_rsa
        chmod 600 /.ssh/id_rsa
    fi

    debug_cmd git config --list
}

function plan() {

    local PLAN_OUT_ARG
    if [[ -n "$PLAN_OUT" ]]; then
        PLAN_OUT_ARG="-out=$PLAN_OUT"
    else
        PLAN_OUT_ARG=""
    fi

    # shellcheck disable=SC2086
    debug_log terraform plan -input=false -no-color -detailed-exitcode -lock-timeout=300s $PARALLEL_ARG $PLAN_OUT_ARG '$PLAN_ARGS'  # don't expand PLAN_ARGS

    set +e
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && terraform plan -input=false -no-color -detailed-exitcode -lock-timeout=300s $PARALLEL_ARG $PLAN_OUT_ARG $PLAN_ARGS) \
        2>"$STEP_TMP_DIR/terraform_plan.stderr" \
        | $TFMASK \
        | tee /dev/fd/3 "$STEP_TMP_DIR/terraform_plan.stdout" \
        | compact_plan \
            >"$STEP_TMP_DIR/plan.txt"

    # shellcheck disable=SC2034
    PLAN_EXIT=${PIPESTATUS[0]}
    set -e
}

function destroy() {
    # shellcheck disable=SC2086
    debug_log terraform destroy -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG $PLAN_ARGS

    set +e
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && terraform destroy -input=false -no-color -auto-approve -lock-timeout=300s $PARALLEL_ARG $PLAN_ARGS) \
        2>"$STEP_TMP_DIR/terraform_destroy.stderr" \
        | tee /dev/fd/3 \
            >"$STEP_TMP_DIR/terraform_destroy.stdout"

    # shellcheck disable=SC2034
    DESTROY_EXIT=${PIPESTATUS[0]}
    set -e
}

function force_unlock() {
    echo "Unlocking state with ID: $INPUT_LOCK_ID"
    debug_log terraform force-unlock -force $INPUT_LOCK_ID
    (cd "$INPUT_PATH" && terraform force-unlock -force $INPUT_LOCK_ID)
}

# Every file written to disk should use one of these directories
STEP_TMP_DIR="/tmp"
JOB_TMP_DIR="$HOME/.dflook-terraform-github-actions"
WORKSPACE_TMP_DIR=".dflook-terraform-github-actions/$(random_string)"
readonly STEP_TMP_DIR JOB_TMP_DIR WORKSPACE_TMP_DIR
export STEP_TMP_DIR JOB_TMP_DIR WORKSPACE_TMP_DIR

function fix_owners() {
    debug_cmd ls -la "$GITHUB_WORKSPACE"
    if [[ -d "$GITHUB_WORKSPACE/.dflook-terraform-github-actions" ]]; then
        chown -R --reference "$GITHUB_WORKSPACE" "$GITHUB_WORKSPACE/.dflook-terraform-github-actions" || true
        debug_cmd ls -la "$GITHUB_WORKSPACE/.dflook-terraform-github-actions"
    fi

    debug_cmd ls -la "$HOME"
    if [[ -d "$HOME/.dflook-terraform-github-actions" ]]; then
        chown -R --reference "$HOME" "$HOME/.dflook-terraform-github-actions" || true
        debug_cmd ls -la "$HOME/.dflook-terraform-github-actions"
    fi
    if [[ -d "$HOME/.terraform.d" ]]; then
        chown -R --reference "$HOME" "$HOME/.terraform.d" || true
        debug_cmd ls -la "$HOME/.terraform.d"
    fi

    if [[ -d "$INPUT_PATH" ]]; then
        debug_cmd find "$INPUT_PATH" -regex '.*/zzzz-dflook-terraform-github-actions-[0-9]+\.auto\.tfvars' -print -delete || true
    fi
}

trap fix_owners EXIT
