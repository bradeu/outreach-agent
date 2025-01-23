#!/bin/bash

# Exit on error
set -e

echo "Building Docker image..."
docker build -t server-chunking-app -f DockerFile .

echo "Starting container..."
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY=${OPENAI_API_KEY:-your_key} \
  -e PINECONE_API_KEY=${PINECONE_API_KEY:-your_key} \
  server-chunking-app

echo "Container started successfully!"
echo "API is accessible at http://localhost:8000"