from fastapi import APIRouter, Request, HTTPException
import uuid
import logging
import math
import time
try:
    from ..helper.pinecone import db_helper_obj
    from ..inference import inference_obj
except ImportError:
    from helper.pinecone import db_helper_obj
    from inference import inference_obj
try:
    from ..celery_app import celery_app
except ImportError:
    from celery_app import celery_app

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

@router.get("/entity/")
async def get_entity(request: Request):
    """
    Query the vector database for entities matching the provided text.
    
    Uses GET method for retrieval operations.
    """

    try:
        data = await request.json()
        text = data.get("text")

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        start_time = time.time()
        res = await inference_obj.query_workflow(text)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Query execution time: {execution_time} seconds")

        return res
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/entity/")
async def create_entity(request: Request):
    """
    Store text in the vector database, automatically handling batching.
    
    Uses POST method for creation operations.
    """

    try:
        data = await request.json()
        text = data.get("text")

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        start_time = time.time()
        sentences = await db_helper_obj.split_text_into_sentences(text)
        vector = await db_helper_obj.embed_sentences_openai(sentences)
        res = await db_helper_obj.upsert_method(vector)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Execution time: {execution_time} seconds")

        return res
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Check the status of a Celery task.
    
    Args:
        task_id: The ID of the Celery task
    
    Returns:
        Dict with task status and result if available
    """
    try:
        task = celery_app.AsyncResult(task_id)
        
        response = {
            "task_id": task_id,
            "status": task.status,
        }
        
        if task.status == 'SUCCESS':
            response["result"] = task.result
        
        if task.status == 'FAILURE':
            response["error"] = str(task.result)
            
        return response
    except Exception as e:
        logger.error(f"Error checking task status: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking task status: {str(e)}")
