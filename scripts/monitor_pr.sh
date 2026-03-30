#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/monitor_pr.sh [PR_NUMBER] [owner/repo] [interval_seconds]
# Example: ./scripts/monitor_pr.sh 883 Kane610/deconz 30

PR_NUMBER="${1:-883}"
REPO="${2:-Kane610/deconz}"
INTERVAL="${3:-30}"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install from https://cli.github.com/ and authenticate (gh auth login)."
  exit 2
fi

echo "Monitoring PR #${PR_NUMBER} in ${REPO} (checking every ${INTERVAL}s). Press Ctrl-C to stop."
while true; do
  echo "=== $(date) ==="
  # Print a readable PR summary (fallback to plain view if JSON fails)
  if ! gh pr view "${PR_NUMBER}" --repo "${REPO}" --json number,title,state,headRefName 2>/dev/null | jq -r '. as $p | "PR #" + ($p.number|tostring) + ": " + $p.title + " (" + $p.state + ") — branch: " + ($p.headRefName // "unknown")'; then
    gh pr view "${PR_NUMBER}" --repo "${REPO}" || true
  fi

  BRANCH=$(gh pr view "${PR_NUMBER}" --repo "${REPO}" --json headRefName -q '.headRefName' 2>/dev/null || true)
  if [ -n "${BRANCH}" ] && [ "${BRANCH}" != "null" ]; then
    echo "Recent workflow runs for branch: ${BRANCH}"
    gh run list --repo "${REPO}" --branch "${BRANCH}" --limit 5 || true
  fi

  sleep "${INTERVAL}"
done
