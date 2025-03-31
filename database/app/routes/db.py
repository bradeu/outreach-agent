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


@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str, query: str, limit: int = 10):
    """
    Query the vector database for entities matching the provided text.
    
    Uses GET method for retrieval operations.
    """
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        if not entity_id:
            raise HTTPException(status_code=400, detail="Entity ID is required")

        start_time = time.time()
        print(entity_id)
        set_namespace(entity_id) # entity_id is the namespace
        res = await inference_obj.query_workflow(query)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Query execution time: {execution_time} seconds")

        return res
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/entities/{entity_id}")
async def create_entity(entity_id: str, request: Request):
    """
    Store text in the vector database, automatically handling batching.
    
    Uses POST method for creation operations.
    """

    try:
        data = await request.json()
        text = data.get("text")
        entity_type = data.get("entity_type")
        namespace = entity_id

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


@router.get("/entities/person/")
async def get_entities(personName: str):
    """
    Get person's entity_id from the vector database.
    
    Uses GET method for retrieval operations.
    """
    try:
        if not personName:
            raise HTTPException(status_code=400, detail="Person name is required")

        start_time = time.time()
        set_namespace("person")
        res = await inference_obj.query_workflow(personName)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Query execution time: {execution_time} seconds")

        return res
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/company/")
async def get_entities(companyName: str):
    """
    Get company's entity_id from the vector database.
    
    Uses GET method for retrieval operations.
    """
    try:
        if not companyName:
            raise HTTPException(status_code=400, detail="Company name is required")

        start_time = time.time()
        set_namespace("company")
        res = await inference_obj.query_workflow(companyName)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Query execution time: {execution_time} seconds")

        return res
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))