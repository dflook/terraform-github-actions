#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup
init-test

exec 3>&1

function set-test-args() {
    TEST_ARGS=""

    if [[ -v INPUT_CLOUD_RUN && -n "$INPUT_CLOUD_RUN" ]]; then
        # I have no idea what this does, it is not well documented.
        TEST_ARGS="$TEST_ARGS -cloud-run=$INPUT_CLOUD_RUN"
    fi

    if [[ -n "$INPUT_TEST_DIRECTORY" ]]; then
        TEST_ARGS="$TEST_ARGS -test-directory=$INPUT_TEST_DIRECTORY"
    fi

    if [[ -n "$INPUT_TEST_FILTER" ]]; then
        for file in $(echo "$INPUT_TEST_FILTER" | tr ',' '\n'); do
            TEST_ARGS="$TEST_ARGS -filter=$file"
        done
    fi

    if [[ "$TOOL_COMMAND_NAME" == "terraform" && $TERRAFORM_VER_MAJOR -ge 1 && $TERRAFORM_VER_MINOR -ge 11 ]]; then
        TEST_ARGS="$TEST_ARGS -junit-xml=$STEP_TMP_DIR/test-result.xml"
    fi
}

function test() {

    debug_log $TOOL_COMMAND_NAME test -no-color "$TEST_ARGS" "$VARIABLE_ARGS"

    set +e
    # shellcheck disable=SC2086
    (cd "$INPUT_PATH" && $TOOL_COMMAND_NAME test -no-color $TEST_ARGS $VARIABLE_ARGS) \
        2>"$STEP_TMP_DIR/terraform_test.stderr" \
        | tee /dev/fd/3 \
            >"$STEP_TMP_DIR/terraform_test.stdout"

    # shellcheck disable=SC2034
    TEST_EXIT=${PIPESTATUS[0]}
    set -e

    cat "$STEP_TMP_DIR/terraform_test.stderr"

    if [[ -f "$STEP_TMP_DIR/test-result.xml" ]]; then
      mkdir -p "$GITHUB_WORKSPACE/$WORKSPACE_TMP_DIR"
      cp "$STEP_TMP_DIR/test-result.xml" "$GITHUB_WORKSPACE/$WORKSPACE_TMP_DIR/test-result.xml"
      set_output junit-xml-path "$WORKSPACE_TMP_DIR/test-result.xml"
    fi

    if [[ $TEST_EXIT -eq 0 ]]; then
        # Workaround a bit of stupidity in the terraform test command
        if grep -q "Success! 0 passed, 0 failed." "$STEP_TMP_DIR/terraform_test.stdout"; then
            error_log "No tests found"
            set_output failure-reason no-tests
            exit 1
        fi
    else
        set_output failure-reason tests-failed
        exit 1
    fi
}

set-test-args
set-variable-args

test
