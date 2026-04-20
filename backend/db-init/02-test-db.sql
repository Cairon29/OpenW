-- Create test database for pytest suite. Idempotent.
-- Runs automatically on first Postgres init (empty volume).
-- For existing volumes, run manually:
--   docker compose exec db psql -U "$DB_USER" -f /docker-entrypoint-initdb.d/02-test-db.sql

SELECT 'CREATE DATABASE "OpenW_test"'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'OpenW_test')\gexec

\c OpenW_test
CREATE EXTENSION IF NOT EXISTS vector;
