from fastapi import APIRouter, Request, HTTPException
import uuid
import logging
import math
import time
try:
    from ..helper.pinecone import db_helper_obj
    from ..inference import inference_obj
    from ..helper.namespace import set_namespace
except ImportError:
    from helper.pinecone import db_helper_obj
    from inference import inference_obj
    from helper.namespace import set_namespace
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
        namespace = data.get("namespace")

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        if not namespace:
            raise HTTPException(status_code=400, detail="Namespace is required")

        start_time = time.time()
        set_namespace(namespace)
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
        entity_type = data.get("entity_type")
        namespace = data.get("namespace")

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        if not entity_type:
            raise HTTPException(status_code=400, detail="Entity type is required")

        if not namespace:
            raise HTTPException(status_code=400, detail="Namespace is required")

        start_time = time.time()
        sentences = await db_helper_obj.split_text_into_sentences(text)
        vector = await db_helper_obj.embed_sentences_openai(sentences)
        logger.info(f"successfully embedded sentences")
        res = await db_helper_obj.upsert_method(vector_list=vector, namespace=namespace, entity_type=entity_type)
        logger.info(f"successfully upserted sentences")
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Execution time: {execution_time} seconds")

        return res
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.patch("/entity/{entity_id}")
async def update_entity(entity_id: str, request: Request):
    """
    Update specific fields of an entity in the vector database.
    
    Uses PATCH method for partial update operations.
    """
    try:
        data = await request.json()
        text = data.get("text")
        
        if not text:
            raise HTTPException(status_code=400, detail="Update data is required")
            
        start_time = time.time()    

        res = await db_helper_obj.update_method(entity_id, text)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Update execution time: {execution_time} seconds")
        
        return res
    except Exception as e:
        logger.error(f"Error in update: {e}")
        raise HTTPException(status_code=500, detail=str(e))
