#!/bin/sh



RUN python manage.py collectstatic --noinput

echo "Django models migration"
python manage.py migrate --noinput

echo "Django collect static"
python manage.py collectstatic --noinput

echo "Starting gunicorn service"
exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application
