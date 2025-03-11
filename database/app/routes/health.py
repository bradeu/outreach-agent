from fastapi import APIRouter, Depends, HTTPException
import time
from datetime import datetime
import logging
try:
    from ..helper.pinecone import db_helper_obj
except ImportError:
    from helper.pinecone import db_helper_obj

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/health")

@router.get("/")
async def health_check():
    """
    Basic health check endpoint that returns the service status and uptime.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "database-api"
    }

@router.get("/pinecone")
async def pinecone_health():
    """
    Check the health of the Pinecone connection.
    """
    try:
        start_time = time.time()
        index = db_helper_obj.get_pinecone_index()
        end_time = time.time()
        
        return {
            "status": "connected",
            "latency_ms": round((end_time - start_time) * 1000, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Pinecone health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Pinecone connection failed: {str(e)}")

@router.get("/readiness")
async def readiness_check():
    """
    Comprehensive readiness check that verifies all dependencies are available.
    """
    issues = []
    status = "ready"
    
    try:
        index = db_helper_obj.get_pinecone_index()
    except Exception as e:
        issues.append(f"Pinecone: {str(e)}")
        status = "not_ready"
    
    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "pinecone": "ok" if "Pinecone" not in str(issues) else "failed",
        },
        "issues": issues
    }
