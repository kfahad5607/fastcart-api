#!/bin/bash

# Run Alembic migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Run seeding script
echo "Running seeding script..."
python3 -m seeds.products -n 200
python3 -m seeds.orders -n 200

# Start the FastAPI app
echo "Starting FastAPI app..."
uvicorn main:app --host 0.0.0.0 --port 8000
