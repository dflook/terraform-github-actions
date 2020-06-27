#!/bin/bash

source /usr/local/actions.sh

debug
setup

EXIT_CODE=0
for file in $(terraform fmt -recursive -no-color -check "$INPUT_PATH"); do
    echo "::error file=$INPUT_PATH/$file::File is not in canonical format (terraform fmt)"
    EXIT_CODE=1
done

if [[ "$EXIT_CODE" -eq 0 ]]; then
    echo "All terraform configuration files are formatted correctly."
fi

exit $EXIT_CODE
