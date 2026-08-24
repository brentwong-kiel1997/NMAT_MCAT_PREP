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

# MiniMax study tutor secrets (never stored in git)
if [[ -f /home/ubuntu/runtime/secrets/load-minimax.sh ]]; then
  # shellcheck disable=SC1091
  source /home/ubuntu/runtime/secrets/load-minimax.sh
elif [[ -f /home/ubuntu/runtime/secrets/minimax.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source /home/ubuntu/runtime/secrets/minimax.env
  set +a
fi

cd "$DEPLOY"

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi

"${VENV}/bin/pip" install -q --upgrade pip
"${VENV}/bin/pip" install -q -r requirements.txt

# --- Two separate SQLite files under $RUNTIME ---
# users.sqlite3     (default): auth / sessions / learner progress
# knowledge.sqlite3 (knowledge): curriculum / notes / practice / diseases
"${VENV}/bin/python" manage.py migrate --database=default --noinput
# Only migrate the knowledge app into the knowledge DB (avoids auth tables there)
"${VENV}/bin/python" manage.py migrate knowledge --database=knowledge --noinput
"${VENV}/bin/python" manage.py load_knowledge
"${VENV}/bin/python" manage.py ensure_admin
"${VENV}/bin/python" manage.py db_status
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
