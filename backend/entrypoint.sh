#!/bin/sh

# Exit immediately if a command fails
set -e

# Use provided environment variables or fallbacks
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}

# Wait for the database service to be ready
echo "--- Waiting for database to be ready at $DB_HOST:$DB_PORT... ---"
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "--- Database is ready! ---"

# Start Gunicorn server
echo "--- Starting Gunicorn... ---"
exec gunicorn \
  --timeout 310 \
  --graceful-timeout 310 \
  --workers 4 \
  --bind 0.0.0.0:2222 \
  "app:create_app()"