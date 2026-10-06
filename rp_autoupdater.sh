#!/bin/sh

set -e

PROJECT_DIR="/srv/rp/ReceiptParser"

echo "+===================================+"
echo "|         Starting deployment       |"
echo "+===================================+"

cd "$PROJECT_DIR"

echo "Stopping Docker Compose services..."
docker compose down

echo "Pulling latest code..."
git pull origin master

echo "Building Docker images..."
docker compose build

echo "Starting up Receipt Parser..."
docker compose up -d

echo "+===================================+"
echo "| Deployment completed successfully |"
echo "+===================================+"
