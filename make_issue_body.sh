#!/bin/sh

set -eu

# Expect RUN_ID to be passed as an environment variable:
# RUN_ID=1234 ./make_issue_body.sh
: "${RUN_ID:?RUN_ID environment variable is required}"

OUT_DIR="out/info"
OUT_FILE="$OUT_DIR/issue_body.md"
LOG_FILE="out/logs/check_result.log"

mkdir -p "$OUT_DIR"

{
    echo "# Hello, this is DataChecker"
    echo
    cat "$LOG_FILE"
    echo
    echo
    echo "Get the HTML-Table for the Homepage [from the artifacts of this workflow run](https://github.com/lsteinmann/Miletus_Bibliography/actions/runs/$RUN_ID )."
} > "$OUT_FILE"

echo "Created $OUT_FILE"