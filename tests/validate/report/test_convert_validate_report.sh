#!/usr/bin/env bash

set +e

VALIDATE_OUTPUT=$(cat tests/validate/report/non_json.txt | python3 image/tools/convert_validate_report.py)
if [[ $? -ne 1 ]]; then
  echo "Expected a failure code"
  exit 1
fi

if [[ "$VALIDATE_OUTPUT" != *""* ]]; then
  echo "Non json was not passed through"
  exit 1
fi

VALIDATE_OUTPUT=$(cat tests/validate/report/valid.json | python3 image/tools/convert_validate_report.py)
if [[ $? -ne 0 ]]; then
  echo "Expected a success code"
  exit 1
fi

if [[ "$VALIDATE_OUTPUT" != "" ]]; then
  echo "Unexpected output"
  exit 1
fi

VALIDATE_OUTPUT=$(cat tests/validate/report/error.json | python3 image/tools/convert_validate_report.py)
if [[ $? -ne 1 ]]; then
  echo "Expected a failure code"
  exit 1
fi

if [[ "$VALIDATE_OUTPUT" != *"::error ::provider.null: no suitable version installed"* ]]; then
  echo "Error has not been formatted correctly"
  exit 1
fi

VALIDATE_OUTPUT=$(cat tests/validate/report/file_location.json | python3 image/tools/convert_validate_report.py)
if [[ $? -ne 1 ]]; then
  echo "Expected a failure code"
  exit 1
fi

if [[ "$VALIDATE_OUTPUT" != *"::error file=main.tf,line=2,col=1::Duplicate resource \"null_resource\" configuration"* ]]; then
  echo "Error has not been formatted correctly"
  exit 1
fi

echo "Done"