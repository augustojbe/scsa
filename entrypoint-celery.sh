#!/bin/sh
set -e

python manage.py wait_for_db

if [ "${CELERY_ROLE:-worker}" = "beat" ]; then
    exec celery -A core beat --loglevel=info
else
    exec celery -A core worker --loglevel=info --concurrency=2
fi
