#!/bin/bash

source /usr/local/actions.sh

debug
setup
init-backend

WS_TMP_DIR=$HOME/$GITHUB_RUN_ID-$(random_string)
rm -rf "$WS_TMP_DIR"
mkdir -p "$WS_TMP_DIR"

set +e
(cd "$INPUT_PATH" && terraform workspace list -no-color) \
    2>"$WS_TMP_DIR/list_err.txt" \
     >"$WS_TMP_DIR/list_out.txt"

readonly TF_WS_LIST_EXIT=${PIPESTATUS[0]}
set -e

if [[ "$ACTIONS_STEP_DEBUG" == "true" ]]; then
  echo "terraform workspace list: ${TF_WS_LIST_EXIT}"
  cat "$WS_TMP_DIR/list_err.txt"
  cat "$WS_TMP_DIR/list_out.txt"
fi

if [[ $TF_WS_LIST_EXIT -ne 0 ]]; then
  echo "Error: Failed to list workspaces"
  exit 1
fi

if workspace_exists "$INPUT_WORKSPACE" <"$WS_TMP_DIR/list_out.txt"; then
  echo "Workspace appears to exist, selecting it"
  (cd "$INPUT_PATH" && terraform workspace select -no-color "$INPUT_WORKSPACE")
else
  echo "Workspace does not appear to exist, attempting to create it"

  set +e
  (cd "$INPUT_PATH" && terraform workspace new -no-color -lock-timeout=300s "$INPUT_WORKSPACE") \
      2>"$WS_TMP_DIR/new_err.txt" \
       >"$WS_TMP_DIR/new_out.txt"

  readonly TF_WS_NEW_EXIT=${PIPESTATUS[0]}
  set -e

  if [[ "$ACTIONS_STEP_DEBUG" == "true" ]]; then
    echo "terraform workspace new: ${TF_WS_NEW_EXIT}"
    cat "$WS_TMP_DIR/new_err.txt"
    cat "$WS_TMP_DIR/new_out.txt"
  fi

  if [[ $TF_WS_NEW_EXIT -ne 0 ]]; then

    if grep -Fq "already exists" "$WS_TMP_DIR/new_err.txt"; then
      echo "Workspace does exist, selecting it"
      (cd "$INPUT_PATH" && terraform workspace select -no-color "$INPUT_WORKSPACE")
    else
      cat "$WS_TMP_DIR/new_err.txt"
      cat "$WS_TMP_DIR/new_out.txt"
      exit 1
    fi
  else
    cat "$WS_TMP_DIR/new_err.txt"
    cat "$WS_TMP_DIR/new_out.txt"
  fi

fi
