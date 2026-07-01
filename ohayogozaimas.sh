#!/bin/sh

echo "Django models migration"
python manage.py migrate --noinput

echo "Django collect static"
python manage.py collectstatic --noinput

echo "Starting gunicorn service"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000