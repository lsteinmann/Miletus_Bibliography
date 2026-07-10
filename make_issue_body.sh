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
    echo "Once this workflow run is finished, there will be [a new release draft](https://github.com/Miletus-Excavation/Miletus_Bibliography/releases/) waiting for your approval."
    echo "It will only be available publicly after your publish it."
    echo 
    echo "Please check the log file here and update the HTML-Table on the Miletus Homepage:"
    echo "You can download the table ('html') [from the artifacts of this workflow run](https://github.com/Miletus-Excavation/Miletus_Bibliography/actions/runs/$RUN_ID)."
    echo
    echo 
    echo "## Data Quality Report for v$(date '+%-m-%Y')"
    echo
    sed -E 's/^([A-Z0-9]{8}): (.*)$/[\1: \2](https:\/\/www.zotero.org\/groups\/4475959\/milet_bibliography\/items\/\1)/' "$LOG_FILE"
    echo 
    echo "-----------------------------------------------------------------------"
    echo
    echo "Thanks for checking and kolay gelsin!"
} > "$OUT_FILE"

echo "Created $OUT_FILE"