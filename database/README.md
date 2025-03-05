# Database Service

A FastAPI application that provides vector database operations with Pinecone, optimized for handling large batches of data.

## Features

- **Query API**: Semantic search against Pinecone vector database
- **Upsert API**: Store text data in Pinecone with automatic batching
- **Asynchronous Processing**: Handles large datasets efficiently using Celery
- **Batch Processing**: Automatically splits large datasets into 1000-record batches (Pinecone's limit)
- **Task Tracking**: Monitor the status of processing tasks
- **RESTful API Design**: Clean API structure following REST principles
- **Health Monitoring**: Comprehensive health check endpoints for monitoring service status

## Getting Started

### Prerequisites

- Python 3.9+
- Redis (for Celery task queue)
- Pinecone account and API key
- OpenAI API key

### Installation

1. Clone the repository
2. Create a `.env` file in the `app/` directory with your API keys:
   ```
   PINECONE_API_KEY=your_pinecone_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Start Redis (required for Celery):
   ```
   docker run -d -p 6379:6379 redis:alpine
   ```
5. Start the Celery worker:
   ```
   cd app/
   celery -A celery_app worker --loglevel=info
   ```
6. Start the FastAPI application:
   ```
   cd app/
   fastapi dev main.py
   ```

## API Endpoints

The API follows RESTful principles with resource-based URLs and HTTP methods to differentiate operations.

### Root Endpoint

```
GET /
```

Returns basic API information and available endpoints.

### Entity Endpoints

#### Query Entities (GET)

```
GET /api/v1/entity/
```

Performs semantic search against the vector database.

**Request Body:**

```json
{
  "text": "Your search query here"
}
```

#### Create Entities (POST)

```
POST /api/v1/entity/
```

Stores text in the vector database, automatically handling batching for large datasets.

**Request Body:**

```json
{
  "text": "Your text to store in the database"
}
```

**Response:**

```json
{
  "status": "processing",
  "message": "Processing 2500 sentences in 3 batches",
  "group_task_id": "task-group-id",
  "batch_task_ids": ["task-id-1", "task-id-2", "task-id-3"]
}
```

#### Update Entity (PATCH)

```
PATCH /api/v1/entity/{entity_id}
```

Updates specific fields of an entity in the vector database.

**Request Body:**

```json
{
  "text": "Updated text for the entity"
}
```

**Response:**

Returns the result of the update operation, typically including confirmation of the update and any relevant metadata.

### Health Check Endpoints

#### Basic Health Check

```
GET /api/v1/health/
```

Returns the basic service status.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2023-07-01T12:34:56.789Z",
  "service": "database-api"
}
```

#### Pinecone Health Check

```
GET /api/v1/health/pinecone
```

Checks the connection to Pinecone.

**Response:**

```json
{
  "status": "connected",
  "latency_ms": 123.45,
  "timestamp": "2023-07-01T12:34:56.789Z"
}
```

#### Redis Health Check

```
GET /api/v1/health/redis
```

Checks the connection to Redis.

**Response:**

```json
{
  "status": "connected",
  "latency_ms": 12.34,
  "timestamp": "2023-07-01T12:34:56.789Z"
}
```

#### Readiness Check

```
GET /api/v1/health/readiness
```

Comprehensive check of all dependencies.

**Response:**

```json
{
  "status": "ready",
  "timestamp": "2023-07-01T12:34:56.789Z",
  "checks": {
    "pinecone": "ok",
    "redis": "ok"
  },
  "issues": []
}
```

## Batch Processing System

The application implements a sophisticated batch processing system to handle Pinecone's limit of 1000 records per upsert:

1. When text is submitted to the entity endpoint (POST), it's split into sentences
2. Sentences are processed in batches of 1000
3. Each batch is processed asynchronously using Celery tasks
4. A tracking task monitors the progress of all batches
5. The API returns task IDs that can be used to check processing status

This approach allows for efficient processing of large datasets while respecting Pinecone's limitations.

## API Documentation

Interactive API documentation is available at:

- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`
- OpenAPI JSON: `/api/openapi.json`

## Docker Deployment

You can also run the application using Docker:

```
docker-compose up -d
```

This will start:

- The FastAPI application
- Redis for the task queue
- Celery workers for processing tasks

## Troubleshooting

- If tasks are not being processed, ensure Redis and Celery workers are running
- Check Celery logs for detailed error information
- Verify your Pinecone and OpenAI API keys are correct in the .env file
- Use the health check endpoints to verify service dependencies

## License

[MIT License](LICENSE)
