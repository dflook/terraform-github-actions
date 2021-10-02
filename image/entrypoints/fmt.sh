#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup

terraform fmt -recursive -no-color "$INPUT_PATH"
