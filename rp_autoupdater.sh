#!/bin/sh

set -e

PROJECT_DIR="/srv/rp/ReceiptParser"
PYLINT_THRESHOLD=8.0

echo "+===================================+"
echo "|         Starting deployment       |"
echo "+===================================+"

cd "$PROJECT_DIR"

echo "Running Pylint check..."

PYLINT_OUTPUT=$(pylint receipt_parser --score=y 2>&1) || true

echo "$PYLINT_OUTPUT"

PYLINT_SCORE=$(printf '%s\n' "$PYLINT_OUTPUT" |
    sed -n 's/.*rated at \([-0-9.]*\)\/10.*/\1/p' |
    tail -n 1)

if [ -z "$PYLINT_SCORE" ]; then
    echo "WARNING: Could not determine Pylint score."
elif [ "$(printf '%s\n' "$PYLINT_SCORE $PYLINT_THRESHOLD" |
    awk '{ if ($1 < $2) print "below"; else print "ok" }')" = "below" ]; then
    echo "WARNING: Pylint score is $PYLINT_SCORE/10 below $PYLINT_THRESHOLD threshold"
else
    echo "Pylint score: $PYLINT_SCORE/10"
fi

echo "Stopping Docker Compose services..."
docker compose down

echo "Pulling latest code..."
git pull origin master

echo "Building Docker images..."
docker compose build

VERSION=$(head -n 1 CHANGELOG.md | sed 's/\*\*//g')

echo "Starting up Receipt Parser ver $VERSION..."

if [ -n "$1" ]; then
    docker compose up
else
    docker compose up -d

    echo "+===================================+"
    echo "| Deployment completed successfully |"
    echo "+===================================+"
fi
