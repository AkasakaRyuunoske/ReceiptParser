#!/bin/sh

echo "Stopping apache2... (never works tho)"
systemctl stop apache2

echo "Django models migration..."
python manage.py migrate --noinput

echo "Django collect static..."
python manage.py collectstatic --noinput

echo "Django load fixtures..."
python manage.py loaddata receipt_parser/fixtures/payment_methods.json

echo "Starting gunicorn service..."
exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application
