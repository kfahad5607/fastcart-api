#!/bin/bash

echo "🚀 Setting up test database..."

# Start the test DB container if not running
if [ ! "$(docker ps -q -f name=test_postgres_db)" ]; then
    echo "📦 Starting test database..."
    docker compose -f docker-compose.test.yml up -d
    sleep 5  # Wait for DB to be ready
fi

# Run migrations
echo "📜 Applying migrations..."
TESTING=1 alembic -x db_url="postgresql+asyncpg://testuser:testpass@localhost:5433/test_db" upgrade head

# Seed some test data
echo "🌱 Seeding test data..."
python3 -m seeds.products -n 10 --clear_existing
python3 -m seeds.orders -n 10 --clear_existing

echo "✅ Test database ready!"
