#!/bin/bash

echo "🧹 Cleaning up test database..."

# Stop & remove the container
docker compose -f docker-compose.test.yml down

echo "✅ Test database cleaned up!"