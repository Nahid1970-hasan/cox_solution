#!/usr/bin/env bash
# Render (and similar) production start: apply migrations then run the app.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1
python manage.py migrate --noinput
exec gunicorn backend_project.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --access-logfile - \
  --error-logfile -
