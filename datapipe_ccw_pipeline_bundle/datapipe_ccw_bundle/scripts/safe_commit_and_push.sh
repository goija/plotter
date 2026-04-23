#!/usr/bin/env bash
set -euo pipefail
MSG="${1:?Usage: safe_commit_and_push.sh <message>}"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
if git diff --cached --quiet; then
  echo "No changes to commit"
  exit 0
fi

git commit -m "$MSG"
git fetch origin main
git pull --rebase --autostash origin main
git push origin HEAD:main
