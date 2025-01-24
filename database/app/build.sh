#!/bin/bash

# Exit on error
set -e

echo "Building and starting containers with docker-compose..."
docker-compose up --build -d

echo "Container started successfully!"
echo "API is accessible at http://localhost:8000"

# Print logs
echo "Showing logs (Ctrl+C to exit)..."
docker-compose logs -f