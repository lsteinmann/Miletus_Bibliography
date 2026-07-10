#!/bin/sh

set -eu

# Expect RELEASE_TAG to be passed as an environment variable:
# RELEASE_TAG=v7-2026 ./make_release_body.sh
: "${RELEASE_TAG:?RELEASE_TAG environment variable is required}"

OUT_DIR="out/info"
OUT_FILE="$OUT_DIR/release_body.md"
INFO_SUMMARY="data/info_summary.md"

mkdir -p "$OUT_DIR"

{
    echo "# The Miletus Bibliography ($RELEASE_TAG)"
    echo
    echo "This release and all its files are automatically generated."
    echo
    cat "$INFO_SUMMARY"
    echo
    echo
} > "$OUT_FILE"

echo "Created $OUT_FILE"