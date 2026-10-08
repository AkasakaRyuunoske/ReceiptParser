#!/bin/sh

echo "+========================+"
echo "|  Setting up seaweedfs  |"
echo "+========================+"

echo "Installing awscli..."
sudo apt install awscli

echo "Setting up credentials for seaweedfs s3..."
export AWS_ACCESS_KEY_ID=admin
export AWS_SECRET_ACCESS_KEY=secret

echo "Creating a bucket for seaweedfs s3..."
aws --endpoint-url http://localhost:8333 \
    s3 mb s3://receipt-images

echo "Checking if it was created..."
aws --endpoint-url http://localhost:8333 \
    s3 ls


echo "+========================+"
echo "|  Setting up Django RP  |"
echo "+========================+"

echo "Django models migration..."
python manage.py migrate --noinput

echo "Django collect static..."
python manage.py collectstatic --noinput

echo "Django load fixtures..."
python manage.py loaddata receipt_parser/fixtures/payment_methods.json

echo "Starting gunicorn service..."
exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application
