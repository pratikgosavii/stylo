#!/bin/bash
# Run this on the PRODUCTION server after git pull gives __pycache__ modify/delete conflicts.
# It accepts the remote's deletion of all __pycache__ files and completes the merge.

set -e
cd "$(dirname "$0")/.." || exit 1

echo "Resolving conflicts: accepting deletion of __pycache__ files..."
git diff --name-only --diff-filter=U | while read -r f; do [ -n "$f" ] && git rm -f "$f"; done

echo "Committing merge..."
git commit -m "Merge origin/master; resolve __pycache__ conflicts (keep deleted)"

echo "Done. Push when ready: git push origin master"
