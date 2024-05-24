#!/bin/sh

set -e

if [ -n "$DB_HOST" ]; then
  /web/wait-for-it.sh "$DB_HOST:${DB_PORT:-3306}"
fi

exec "$@"