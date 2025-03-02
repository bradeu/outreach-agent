from fastapi import FastAPI, Request, HTTPException
import uuid
import logging
import time
import math
try:
    from .helper.pinecone import db_helper_obj
    from .inference import inference_obj
except ImportError:
    from helper.pinecone import db_helper_obj
    from inference import inference_obj
from celery import Celery
# from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logger = logging.getLogger(__name__)

celery = Celery("executor",
            backend="redis://localhost:6379/0",
            broker="redis://localhost:6379/0")

app = FastAPI()

@app.get("/")
async def root(request: Request):
    return await request.json()

@app.get("/query/")
async def query_endpoint(request: Request):

    """
    Endpoint to query the agent.
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
        print(f"Execution time: {execution_time} seconds")

        return res
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upsert/")
async def upsert_endpoint(request: Request):
    # data = await request.json()
    # text = data.get("text")

    # start_time = time.time()
    # sentences = await db_helper_obj.split_text_into_sentences(text)
    # vector = await db_helper_obj.embed_sentences_openai(sentences)
    # res = await db_helper_obj.upsert_method(vector)
    # end_time = time.time()
    # execution_time = end_time - start_time
    # print(f"Execution time: {execution_time} seconds")

    # return res

    """
    Endpoint to upsert text to Pinecone, respecting the 1000 record limit.
    Splits large batches into smaller ones and processes them using Celery tasks.
    """

    try:
        task_id = request.headers.get("x-request-id", uuid.uuid4().hex)
        data = await request.json()
        text = data.get("text")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        sentences = await db_helper_obj.split_text_into_sentences(text)
        
        batch_size = 1000
        total_sentences = len(sentences)
        total_batches = math.ceil(total_sentences / batch_size)
        
        logger.info(f"Processing {total_sentences} sentences in {total_batches} batches")
        
        task_ids = []
        
        for i in range(0, total_sentences, batch_size):
            batch = sentences[i:i+batch_size]
            batch_task_id = f"{task_id}_{i//batch_size}"
            
            vector_batch = await db_helper_obj.embed_sentences_openai(batch)
            
            result = celery.send_task(
                "app.tasks.upsert_batch", 
                args=[vector_batch],
                task_id=batch_task_id
            )
            
            task_ids.append(batch_task_id)
            logger.info(f"Queued batch {i//batch_size + 1}/{total_batches} with task ID: {batch_task_id}")
        
        if total_batches > 1:
            group_task = celery.send_task(
                "app.tasks.track_upsert_group",
                args=[task_ids],
                task_id=f"{task_id}_group"
            )
            return {
                "status": "processing",
                "message": f"Processing {total_sentences} sentences in {total_batches} batches",
                "group_task_id": group_task.id,
                "batch_task_ids": task_ids
            }
        else:
            return {
                "status": "processing",
                "message": f"Processing {total_sentences} sentences",
                "task_id": task_ids[0]
            }
            
    except Exception as e:
        logger.error(f"Error in upsert endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Check the status of a Celery task.
    
    Args:
        task_id: The ID of the Celery task
        
    Returns:
        Dict with task status and result if available
    """
    try:
        task = celery.AsyncResult(task_id)
        
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