#!/usr/bin/env bash
set -e

# Optional: show env for debugging (you can remove in prod)
echo "Running entrypoint: DATABASE_URL=${DATABASE_URL:-not set}"

# Run migrations if DATABASE_URL exists
if [ -n "$DATABASE_URL" ]; then
  flask db upgrade || true
fi

# Execute passed CMD (gunicorn by default)
exec "$@"
