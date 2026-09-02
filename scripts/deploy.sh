#!/usr/bin/env bash
# Deploy checkout from bare repo and (re)start Gunicorn WSGI.
set -euo pipefail

APP_NAME="django-wsgi"
DEPLOY="/home/ubuntu/deploy/${APP_NAME}"
RUNTIME="/home/ubuntu/runtime/${APP_NAME}"
BARE="/home/ubuntu/repos/${APP_NAME}.git"
VENV="${RUNTIME}/venv"
LOGS="${RUNTIME}/logs"
SOCK="127.0.0.1:8000"

mkdir -p "$LOGS" "$DEPLOY"

export DJANGO_DEBUG="${DJANGO_DEBUG:-0}"
# no wildcard: keep the Host header pinned to names the server is reached by
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-localhost,127.0.0.1,124.222.115.8,10.0.0.14}"

# Tutor keys are read from .env per request (portal/envfile.py). Drop any model
# credentials inherited from the pushing shell so the server process and its
# children never carry them in /proc/<pid>/environ.
while IFS='=' read -r _name _; do
  case "$_name" in
    MINIMAX_*|OPENAI_API_KEY|OPENAI_BASE_URL|ANTHROPIC_*) unset "$_name" ;;
  esac
done < <(env)

cd "$DEPLOY"

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

# --- Databases under $RUNTIME ---
# users.sqlite3 (default): auth / sessions / learner progress.
# Knowledge content now ships in git as content/ YAML and is read by
# portal/content.py; validate_content gates the deploy before restart.
"${VENV}/bin/python" manage.py migrate --database=default --noinput
"${VENV}/bin/python" manage.py validate_content
"${VENV}/bin/python" manage.py ensure_admin
"${VENV}/bin/python" manage.py ensure_ai_model
"${VENV}/bin/python" manage.py db_status
"${VENV}/bin/python" manage.py env_status
"${VENV}/bin/python" manage.py collectstatic --noinput

# Gunicorn runs as a systemd unit (gunicorn.service) — enabled at boot,
# restarted on failure. deploy.sh only restarts it after a content update.
sudo systemctl restart gunicorn
systemctl is-active --quiet gunicorn

REV="$(git --git-dir="$BARE" rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "Deployed ${REV} → gunicorn ${SOCK}"
