#!/bin/bash

set -e

# Get the directory of this script.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR"

if [ ! -e docs-cn/.git ]; then
  if [ -d "docs-cn" ]; then
    rm -rf docs-cn
  fi
  # Clone the pingcap/website-docs repository.
  git clone https://github.com/pingcap/docs-cn
fi

(
cd docs-cn
TARGET_BRANCH="release-6.5"
git fetch origin $TARGET_BRANCH
git checkout $TARGET_BRANCH
git pull origin $TARGET_BRANCH
git checkout -b "$TARGET_BRANCH-update"
)