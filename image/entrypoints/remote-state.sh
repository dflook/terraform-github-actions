#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug

INPUT_PATH="$STEP_TMP_DIR/remote-state"
export INPUT_PATH

rm -rf "$INPUT_PATH"
mkdir -p "$INPUT_PATH"

cat >"$INPUT_PATH/backend.tf" <<EOF
terraform {
  backend "$INPUT_BACKEND_TYPE" {}
}
EOF

setup
init-backend-workspace
output
