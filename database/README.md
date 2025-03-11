# Database Service

A FastAPI application that provides vector database operations with Pinecone, optimized for handling large batches of data.

## Features

- **Query API**: Semantic search against Pinecone vector database
- **Upsert API**: Store text data in Pinecone with automatic batching
- **Update API**: Updates existing entity in the database
- **Asynchronous Processing**: Handles large datasets efficiently
- **Batch Processing**: Automatically splits large datasets into 1000-record batches (Pinecone's limit)
- **Task Tracking**: Monitor the status of processing tasks
- **RESTful API Design**: Clean API structure following REST principles
- **Health Monitoring**: Comprehensive health check endpoints for monitoring service status

## Getting Started

### Prerequisites

- Python 3.9+
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
4. Start the FastAPI application:
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
  "text": "Your search query here",
  "namespace": "company"
}
```

**Response:**

```json
{
  "results": [
    {
      "entity_id": "145359ee-d959-46dc-a4a6-3587d89bca44",
      "sentence": "Relevant sentence matching your query.",
      "entity_type": "company",
      "namespace": "company",
      "created_at": "2025-03-10T15:15:08.935460"
    },
    {
      "entity_id": "5eadeb84-80b8-44e3-801b-f67e6efefa57",
      "sentence": "Another relevant sentence matching your query.",
      "entity_type": "company",
      "namespace": "company",
      "created_at": "2025-03-10T15:15:08.935814"
    }
  ]
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
  "text": "Your text to store in the database",
  "namespace": "company",
  "entity_type": "company"
}
```

**Response:**

```json
{
  "upserted_count": 7
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
    "pinecone": "ok"
  },
  "issues": []
}
```

## API Documentation

Interactive API documentation is available at:

- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`
- OpenAPI JSON: `/api/openapi.json`

## Docker Deployment

You can also run the application using Docker:

```
# Option 1: Use the build script
./build.sh

# Option 2: Use docker-compose directly
docker-compose up -d
```

This will build and start the FastAPI application.

## Troubleshooting

- Verify your Pinecone and OpenAI API keys are correct in the .env file
- Use the health check endpoints to verify service dependencies

## License

[MIT License](LICENSE)
