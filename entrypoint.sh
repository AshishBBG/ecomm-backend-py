#!/usr/bin/env bash
set -e
# run migrations then start server
if [ -n "$DATABASE_URL" ]; then
  flask db upgrade || true
fi
exec "$@"
