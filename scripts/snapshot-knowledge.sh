#!/usr/bin/env bash
# Rebuild the committed knowledge.sqlite3 snapshot from the Python sources.
#
# The knowledge DB is derived data: portal/notes.py, practice.py,
# materials_data.py, pack_enrich.py, exams.py, diseases.py are the source of
# truth. This script rebuilds the snapshot committed to git so the two can
# never drift apart. Run it after any content change and commit both together.
#
# Usage: scripts/snapshot-knowledge.sh
set -euo pipefail

cd "$(dirname "$0")/.."

VENV="${VENV:-/home/ubuntu/runtime/django-wsgi/venv}"
SNAPSHOT="knowledge.sqlite3"

# Build a pristine DB in place from the committed sources — never copy the
# live runtime file, which Gunicorn may have open.
GABAY_KNOWLEDGE_DB="$PWD/$SNAPSHOT" \
  "$VENV/bin/python" manage.py migrate knowledge --database=knowledge --noinput
GABAY_KNOWLEDGE_DB="$PWD/$SNAPSHOT" \
  "$VENV/bin/python" manage.py load_knowledge --flush

"$VENV/bin/python" - "$SNAPSHOT" <<'PY'
import sqlite3
import sys

conn = sqlite3.connect(sys.argv[1])
print("integrity_check:", conn.execute("PRAGMA integrity_check").fetchone()[0])
for (table,) in sorted(conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")):
    n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {n}")
PY

echo "snapshot written: $SNAPSHOT"
