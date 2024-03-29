#!/bin/bash

set -e

# Get the directory of this script.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR"

REPO_OWNER="Oreoxmt"
REPO_NAME="docs-cn"
TARGET_BRANCHES=("release-6.5" "release-6.1")
TABLE_FILTER="html"

if [ ! -e "$REPO_NAME/.git" ]; then
  if [ -d "$REPO_NAME" ]; then
    rm -rf "$REPO_NAME"
  fi
  git clone "https://github.com/$REPO_OWNER/$REPO_NAME"
fi

for branch in "${TARGET_BRANCHES[@]}"; do
  git -C "$REPO_NAME" fetch origin "$branch"
  git -C "$REPO_NAME" checkout "$branch"
  git -C "$REPO_NAME" pull origin "$branch"
  git -C "$REPO_NAME" checkout -b "$branch-convert-to-grid-table-$(date +%Y%m%d%H%M%S)"
  echo "Start to convert tables in $branch branch"
  python3 worker.py "$TABLE_FILTER" "$REPO_NAME"
  git -C "$REPO_NAME" add .
  git -C "$REPO_NAME" commit -m "Convert HTML tables and pipe tables to grid tables" || echo "No changes to commit"
done
