#!/bin/sh
echo "Waiting for postgres..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "PostgreSQL is up."
exec flask run --host=0.0.0.0 --port=2222
