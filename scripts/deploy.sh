#!/usr/bin/env bash
# Deploy checkout from bare repo and (re)start Gunicorn WSGI.
set -euo pipefail

APP_NAME="django-wsgi"
DEPLOY="/home/ubuntu/deploy/${APP_NAME}"
RUNTIME="/home/ubuntu/runtime/${APP_NAME}"
BARE="/home/ubuntu/repos/${APP_NAME}.git"
VENV="${RUNTIME}/venv"
LOGS="${RUNTIME}/logs"
PIDFILE="${RUNTIME}/gunicorn.pid"
SOCK="127.0.0.1:8000"

mkdir -p "$LOGS" "$DEPLOY"

export DJANGO_DEBUG="${DJANGO_DEBUG:-0}"
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-localhost,127.0.0.1,*}"

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
"${VENV}/bin/pip" install -q -r requirements.txt

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

if [[ -f "$PIDFILE" ]]; then
  OLD_PID="$(cat "$PIDFILE" || true)"
  if [[ -n "${OLD_PID}" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID" || true
    for _ in $(seq 1 20); do
      kill -0 "$OLD_PID" 2>/dev/null || break
      sleep 0.2
    done
    kill -9 "$OLD_PID" 2>/dev/null || true
  fi
  rm -f "$PIDFILE"
fi

"${VENV}/bin/gunicorn" config.wsgi:application \
  --bind "$SOCK" \
  --workers 2 \
  --pid "$PIDFILE" \
  --access-logfile "${LOGS}/gunicorn.access.log" \
  --error-logfile "${LOGS}/gunicorn.error.log" \
  --daemon

REV="$(git --git-dir="$BARE" rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "Deployed ${REV} → gunicorn ${SOCK}"
