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

# Run seed script (idempotent — safe to run on every deploy)
echo "--- Running seed script... ---"
python -m src.db.scripts.seed
echo "--- Seed complete! ---"

# Start Gunicorn server
echo "--- Starting Gunicorn... ---"
exec gunicorn \
  --worker-class gevent \
  --workers 1 \
  --worker-connections 1000 \
  --timeout 310 \
  --graceful-timeout 30 \
  --bind 0.0.0.0:2222 \
  "src:create_app()"
