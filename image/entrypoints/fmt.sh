#!/bin/bash

source /usr/local/actions.sh

debug
setup

terraform fmt -recursive -no-color "$INPUT_PATH" | save_artifact fmt.txt
