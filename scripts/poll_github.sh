#!/usr/bin/env bash
# Poll GitHub for new commits on main and deploy the site when they appear.
#
# Runs from cron every 2 minutes. The bare repo stays the deploy source; this
# script keeps its main ref in sync with GitHub, then replays the exact
# post-receive deploy sequence (checkout + deploy.sh). Deploy state is tracked
# in last_github_deploy: it is only advanced after a successful deploy, so a
# failed deploy is retried on the next tick.
set -euo pipefail

APP_NAME="django-wsgi"
BARE="/home/ubuntu/repos/${APP_NAME}.git"
DEPLOY="/home/ubuntu/deploy/${APP_NAME}"
RUNTIME="/home/ubuntu/runtime/${APP_NAME}"
GITHUB_URL="git@github.com:brentwong-kiel1997/NMAT_MCAT_PREP.git"
BRANCH="main"
STATE="${RUNTIME}/last_github_deploy"
LOG="${RUNTIME}/logs/poll_github.log"

export GIT_SSH_COMMAND="ssh -i ${HOME}/.ssh/id_ed25519 -o BatchMode=yes"

log() { echo "$(date -Is) $*" >>"$LOG"; }

mkdir -p "$RUNTIME/logs"

# One deploy at a time; skip this tick if the previous one is still running.
exec 9>"${RUNTIME}/poll_github.lock"
flock -n 9 || { log "previous poll still running, skipping"; exit 0; }

# BatchMode makes SSH fail fast instead of hanging the cron slot.
if ! git -C "$BARE" fetch -q "$GITHUB_URL" "$BRANCH" 2>>"$LOG"; then
  log "fetch failed (network?) — will retry next tick"
  exit 0
fi

fetched=$(git -C "$BARE" rev-parse FETCH_HEAD)
last=""
[[ -f "$STATE" ]] && last=$(cat "$STATE")

if [[ "$fetched" == "$last" ]]; then
  exit 0
fi

log "new commit ${fetched:0:7} on GitHub (last deployed: ${last:0:7:-none}) — deploying"

# Mirror the post-receive sequence: move main to GitHub's tip, sync the
# checkout, then deploy. Guarded by `if` so a failure retries next tick.
# `9>&-` stops the daemonized Gunicorn from inheriting this script's lock
# fd — an inherited fd would hold the flock forever and stall every poll.
if git -C "$BARE" update-ref "refs/heads/$BRANCH" "$fetched" \
   && GIT_WORK_TREE="$DEPLOY" GIT_DIR="$BARE" git checkout -f "$BRANCH" >>"$LOG" 2>&1 \
   && chmod +x "$DEPLOY/scripts/deploy.sh" \
   && "$DEPLOY/scripts/deploy.sh" >>"$LOG" 2>&1 9>&-; then
  echo "$fetched" >"$STATE"
  log "deployed ${fetched:0:7}"
else
  log "deploy FAILED for ${fetched:0:7} — will retry next tick"
fi
