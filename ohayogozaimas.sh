#!/bin/sh

echo "Stopping apache2..."
systemctl stop apache2

echo "Django models migration..."
python manage.py migrate --noinput

echo "Django collect static..."
python manage.py collectstatic --noinput

echo "Starting gunicorn service..."
exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application
