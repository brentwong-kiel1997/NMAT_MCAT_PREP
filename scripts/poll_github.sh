#!/usr/bin/env bash
# Deploy the site, preferring the local bare repo over GitHub.
#
# Runs from cron every 2 minutes. Priority order:
#   1. LOCAL: if the bare repo's main holds commits GitHub does not have
#      (pushed via `git push deploy main`), those win — the poller must
#      never roll a local deployment back to an older GitHub tip.
#   2. REMOTE: otherwise follow origin/main on GitHub (NMAT_MCAT_PREP).
#
# The bare repo stays the deploy source; the script replays the exact
# post-receive deploy sequence (checkout + deploy.sh). Deploy state is
# tracked in last_deploy: it only advances after a successful deploy, so
# a failed deploy is retried on the next tick.
set -euo pipefail

APP_NAME="django-wsgi"
BARE="/home/ubuntu/repos/${APP_NAME}.git"
DEPLOY="/home/ubuntu/deploy/${APP_NAME}"
RUNTIME="/home/ubuntu/runtime/${APP_NAME}"
GITHUB_URL="git@github.com:brentwong-kiel1997/NMAT_MCAT_PREP.git"
BRANCH="main"
STATE="${RUNTIME}/last_deploy"
LOG="${RUNTIME}/logs/poll_github.log"

export GIT_SSH_COMMAND="ssh -i ${HOME}/.ssh/id_ed25519 -o BatchMode=yes"

log() { echo "$(date -Is) $*" >>"$LOG"; }

mkdir -p "$RUNTIME/logs"

# One deploy at a time; skip this tick if the previous one is still running.
exec 9>"${RUNTIME}/poll_github.lock"
flock -n 9 || { log "previous poll still running, skipping"; exit 0; }

fetched=""
if git -C "$BARE" fetch -q "$GITHUB_URL" "$BRANCH" 2>>"$LOG"; then
  fetched=$(git -C "$BARE" rev-parse FETCH_HEAD)
else
  log "fetch failed (network?) — local-only commits still considered"
fi

local_tip=$(git -C "$BARE" rev-parse "refs/heads/$BRANCH")
last=""
[[ -f "$STATE" ]] && last=$(cat "$STATE")

# Local-first: bare-repo commits that GitHub lacks outrank the remote tip.
target="$fetched"
if [[ -n "$local_tip" && "$local_tip" != "$fetched" ]] \
   && ! git -C "$BARE" merge-base --is-ancestor "$local_tip" "$fetched" 2>/dev/null; then
  target="$local_tip"
fi
if [[ -z "$target" ]]; then
  exit 0
fi

if [[ "$target" == "$last" ]]; then
  exit 0
fi

origin=$([[ "$target" == "$local_tip" ]] && echo local || echo github)
log "new commit ${target:0:7} ($origin, last deployed: ${last:-none}) — deploying"

# Mirror the post-receive sequence: move main to the target, sync the
# checkout, then deploy. Guarded by `if` so a failure retries next tick.
# `9>&-` stops the daemonized Gunicorn from inheriting this script's lock
# fd — an inherited fd would hold the flock forever and stall every poll.
if git -C "$BARE" update-ref "refs/heads/$BRANCH" "$target" \
   && GIT_WORK_TREE="$DEPLOY" GIT_DIR="$BARE" git checkout -f "$BRANCH" >>"$LOG" 2>&1 \
   && chmod +x "$DEPLOY/scripts/deploy.sh" \
   && "$DEPLOY/scripts/deploy.sh" >>"$LOG" 2>&1 9>&-; then
  echo "$target" >"$STATE"
  log "deployed ${target:0:7} ($origin)"
else
  log "deploy FAILED for ${target:0:7} ($origin) — will retry next tick"
fi
