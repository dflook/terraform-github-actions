#!/bin/bash

source /usr/local/actions.sh

debug
setup

EXIT_CODE=0
terraform fmt -recursive -no-color -check -diff "$INPUT_PATH" | while IFS= read -r line; do
    echo "$line"

    if [[ -f "$line" ]]; then
        echo "::error file=$line::File is not in canonical format (terraform fmt)"
        EXIT_CODE=1
    fi
done

if [[ "$EXIT_CODE" -eq 0 ]]; then
    echo "All terraform configuration files are formatted correctly."
fi

exit $EXIT_CODE
