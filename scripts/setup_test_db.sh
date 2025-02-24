#!/bin/bash

echo "🚀 Setting up test database..."

# Read DB_URL from command-line argument
DB_URL=$1

if [[ -z "$DB_URL" ]]; then
    echo "❌ ERROR: DB_URL argument is required!"
    exit 1
fi

# Start the test DB container if not running
if [ ! "$(docker ps -q -f name=test_postgres_db)" ]; then
    echo "📦 Starting test database..."
    docker-compose -f docker-compose.test.yml up -d
fi

# Wait until the PostgreSQL container is in a "healthy" state
MAX_WAIT=30  # Timeout in seconds
WAIT_TIME=0

while true; do
    STATUS=$(docker inspect -f '{{.State.Health.Status}}' test_postgres_db 2>/dev/null)

    if [[ "$STATUS" == "healthy" ]]; then
        echo "✅ Database is ready!"
        break
    fi

    if [[ $WAIT_TIME -ge $MAX_WAIT ]]; then
        echo "❌ ERROR: Timeout waiting for PostgreSQL to become healthy!"
        exit 1
    fi

    sleep 1
    ((WAIT_TIME+=1))
done

# Run migrations
echo "📜 Applying migrations..."
alembic -x db_url=$DB_URL upgrade head

# Seed some test data
echo "🌱 Seeding test data..."
python3 -m seeds.products -n 10 --clear_existing
python3 -m seeds.orders -n 10 --clear_existing

echo "✅ Test database ready!"
