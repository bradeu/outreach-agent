from fastapi import FastAPI, Request, HTTPException
import logging
from celery import Celery
try:
    from .routes import db, health
except ImportError:
    from routes import db, health

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

celery = Celery("executor",
            backend="redis://localhost:6379/0",
            broker="redis://localhost:6379/0")

app = FastAPI(
    title="Vector Database API", 
    description="API for vector database operations with Pinecone",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Vector Database API",
        "version": "1.0.0",
        "endpoints": {
            "entity": "/api/v1/entity/",
            "task": "/api/v1/task/{task_id}",
            "health": "/api/v1/health/",
            "docs": "/api/docs"
        }
    }

app.include_router(db.router, tags=["Database Operations"])
app.include_router(health.router, tags=["Health Checks"])