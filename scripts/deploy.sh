#!/usr/bin/env bash
# Deploy: validate a staging checkout, then atomically swap it live.
#
# The old flow checked out straight into the live directory, so still-running
# workers served the NEW yaml (content.py reads by mtime) during the
# pip/migrate/validate window — a broken push 500'd the site while the gate
# was deciding. Now: checkout lands in $STAGING, checks + migrations run
# there, and only a green build is renamed onto $DEPLOY. Old workers keep
# their cwd on the previous directory inode, so they serve the old, complete
# revision until the restart; rollback is swapping the two directories back.
set -euo pipefail

APP_NAME="django-wsgi"
DEPLOY="/home/ubuntu/deploy/${APP_NAME}"
PREV="/home/ubuntu/deploy/.${APP_NAME}.prev"
RUNTIME="/home/ubuntu/runtime/${APP_NAME}"
BARE="/home/ubuntu/repos/${APP_NAME}.git"
VENV="${RUNTIME}/venv"
LOGS="${RUNTIME}/logs"
SOCK="127.0.0.1:8000"

# this script lives in the fresh checkout that post-receive just created
STAGING="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$LOGS"

export DJANGO_DEBUG="${DJANGO_DEBUG:-0}"
# no wildcard: keep the Host header pinned to names the server is reached by
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-localhost,127.0.0.1,124.222.115.8,10.0.0.14}"

# Tutor/model keys are read from .env per request (portal/envfile.py). Drop
# any model credentials inherited from the pushing shell so neither the
# server process nor its children carry them in /proc/<pid>/environ.
while IFS='=' read -r _name _; do
  case "$_name" in
    MINIMAX_*|OPENAI_API_KEY|OPENAI_BASE_URL|ANTHROPIC_*) unset "$_name" ;;
  esac
done < <(env)

cd "$STAGING"

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi

"${VENV}/bin/pip" install -q --upgrade pip
# prefer the committed lockfile (exact prod parity); fall back to ranges
if [[ -f requirements.lock ]]; then
  "${VENV}/bin/pip" install -q -r requirements.lock
else
  "${VENV}/bin/pip" install -q -r requirements.txt
fi

# --- gate the build in staging BEFORE anything goes live ---
"${VENV}/bin/python" manage.py check
"${VENV}/bin/python" manage.py migrate --database=default --noinput
"${VENV}/bin/python" manage.py validate_content
"${VENV}/bin/python" manage.py collectstatic --noinput

# --- swap: two renames on one filesystem, microseconds wide ---
# a root-owned $PREV (from a sudo-run hook once) must not brick the push
if [[ -d "$DEPLOY" ]]; then
  rm -rf "$PREV" 2>/dev/null || sudo -n rm -rf "$PREV" || true
  mv "$DEPLOY" "$PREV"
fi
# if the second rename fails, put the old tree back — never leave no live dir
mv "$STAGING" "$DEPLOY" || { mv "$PREV" "$DEPLOY" 2>/dev/null || true; exit 1; }
cd "$DEPLOY"

"${VENV}/bin/python" manage.py ensure_admin
"${VENV}/bin/python" manage.py ensure_ai_model
"${VENV}/bin/python" manage.py db_status
"${VENV}/bin/python" manage.py env_status

# Gunicorn runs as a systemd unit (gunicorn.service) — enabled at boot,
# restarted on failure. deploy.sh only restarts it after a green swap.
sudo systemctl restart gunicorn
systemctl is-active --quiet gunicorn

REV="$(git --git-dir="$BARE" rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "Deployed ${REV} → gunicorn ${SOCK}"
