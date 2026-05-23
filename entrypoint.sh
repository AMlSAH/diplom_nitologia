#!/bin/bash
set -e

if [ -n "$REDIS_HOST" ]; then
    echo "Waiting for Redis at $REDIS_HOST:$REDIS_PORT..."
    while ! nc -z "$REDIS_HOST" "${REDIS_PORT:-6379}"; do
        sleep 1
    done
    echo "Redis is up."
fi

python manage.py migrate --noinput

python manage.py collectstatic --noinput --clear 2>/dev/null || true

exec "$@"
