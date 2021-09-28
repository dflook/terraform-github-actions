#!/bin/bash

source /usr/local/actions.sh

debug
setup
init

(cd "$INPUT_PATH" && terraform version -json | convert_version)
