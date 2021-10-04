#!/bin/bash

# shellcheck source=../actions.sh
source /usr/local/actions.sh

debug
setup

terraform fmt -recursive -no-color -check -diff "$INPUT_PATH" | while IFS= read -r line; do
    echo "$line"

    if [[ -f "$line" ]]; then
        if [[ ! -v FAILURE_REASON_SET ]]; then
            FAILURE_REASON_SET=yes
            set_output failure-reason check-failed
        fi

        echo "::error file=$line::File is not in canonical format (terraform fmt)"
    fi
done

# terraform fmt has non zero exit code if there are non canonical files

echo "All terraform configuration files are formatted correctly."
