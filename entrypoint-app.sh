#!/bin/sh
set -e

python manage.py wait_for_db

python manage.py migrate_locked

python manage.py collectstatic --noinput --clear

if [ "${DEBUG:-False}" = "True" ]; then
    exec python manage.py runserver 0.0.0.0:8000
else
    exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
fi
