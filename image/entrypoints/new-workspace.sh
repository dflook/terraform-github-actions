#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup

if [[ "$TERRAFORM_BACKEND_TYPE" == "remote" || "$TERRAFORM_BACKEND_TYPE" == "cloud" ]]; then
    TERRAFORM_VERSION="$TERRAFORM_VER_MAJOR.$TERRAFORM_VER_MINOR.$TERRAFORM_VER_PATCH" terraform-cloud-workspace new "$INPUT_WORKSPACE"
    exit 0
fi

init-backend-default-workspace

set +e
(cd "$INPUT_PATH" && terraform workspace list -no-color) \
    2>"$STEP_TMP_DIR/terraform_workspace_list.stderr" \
    >"$STEP_TMP_DIR/terraform_workspace_list.stdout"

readonly TF_WS_LIST_EXIT=${PIPESTATUS[0]}
set -e

debug_log "terraform workspace list: ${TF_WS_LIST_EXIT}"
debug_file "$STEP_TMP_DIR/terraform_workspace_list.stderr"
debug_file "$STEP_TMP_DIR/terraform_workspace_list.stdout"

if [[ $TF_WS_LIST_EXIT -ne 0 ]]; then
    echo "Error: Failed to list workspaces"
    exit 1
fi

if workspace_exists "$INPUT_WORKSPACE" <"$STEP_TMP_DIR/terraform_workspace_list.stdout"; then
    echo "Workspace appears to exist, selecting it"
    (cd "$INPUT_PATH" && terraform workspace select -no-color "$INPUT_WORKSPACE")
else
    echo "Workspace does not appear to exist, attempting to create it"

    set +e
    (cd "$INPUT_PATH" && terraform workspace new -no-color -lock-timeout=300s "$INPUT_WORKSPACE") \
        2>"$STEP_TMP_DIR/terraform_workspace_new.stderr" \
        >"$STEP_TMP_DIR/terraform_workspace_new.stdout"

    readonly TF_WS_NEW_EXIT=${PIPESTATUS[0]}
    set -e

    debug_log "terraform workspace new: ${TF_WS_NEW_EXIT}"
    debug_file "$STEP_TMP_DIR/terraform_workspace_new.stderr"
    debug_file "$STEP_TMP_DIR/terraform_workspace_new.stdout"

    if [[ $TF_WS_NEW_EXIT -ne 0 ]]; then

        if grep -Fq "already exists" "$STEP_TMP_DIR/terraform_workspace_new.stderr"; then
            echo "Workspace does exist, selecting it"
            (cd "$INPUT_PATH" && terraform workspace select -no-color "$INPUT_WORKSPACE")
        else
            cat "$STEP_TMP_DIR/terraform_workspace_new.stderr"
            cat "$STEP_TMP_DIR/terraform_workspace_new.stdout"
            exit 1
        fi
    else
        cat "$STEP_TMP_DIR/terraform_workspace_new.stderr"
        cat "$STEP_TMP_DIR/terraform_workspace_new.stdout"
    fi

fi
