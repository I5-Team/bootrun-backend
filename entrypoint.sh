#!/bin/bash
set -e

echo "Starting BootRun API Server..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "Redis is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head
echo "Migrations completed!"

# Start the application
echo "Starting application..."
exec "$@"

COPY ./entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

