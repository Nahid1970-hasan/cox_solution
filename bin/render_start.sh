#!/usr/bin/env bash
# Render (and similar) production start: apply migrations then run the app.
# If Render "Start Command" is still "runserver", change it to: bash bin/render_start.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONUNBUFFERED=1
PY="${PYTHON:-python}"
echo "Running migrations from $ROOT ..."
"$PY" manage.py migrate --noinput
echo "Migrations finished."
exec gunicorn backend_project.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --access-logfile - \
  --error-logfile -
