from fastapi import APIRouter, Request, HTTPException
import uuid
import logging
import math
import time
from fastapi.responses import JSONResponse
try:
    from ..helper.pinecone import db_helper_obj
    from ..inference import inference_obj
    from ..helper.global_variable import set_namespace, set_limit
    from ..helper.deduplication import deduplication_obj
except ImportError:
    from helper.pinecone import db_helper_obj
    from inference import inference_obj
    from helper.global_variable import set_namespace, set_limit
    from helper.deduplication import deduplication_obj
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")


@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str, query: str, limit: int):
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
        set_limit(limit)
        res = await inference_obj.query_workflow(query)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Query execution time: {execution_time} seconds")

        return JSONResponse(content={"Results": res}, status_code=200)
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
        namespace = await deduplication_obj.deduplicate_entity_id(entity_id)

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
        logger.info(f"res: {res}")
        return JSONResponse(content={"Message": "Successfully upserted"}, status_code=200)
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entities/entity_id/")
async def get_entity_id():
    """
    Get all of the entity_ids from the vector database.
    
    Uses GET method for retrieval operations.
    """

    logger.info(f"Getting entity_ids")

    try:
        json = {
            "status": "success",
            "entity_ids": await deduplication_obj.get_entity_ids()
        }
        return json
    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entities/person/")
async def get_person_entities(personName: str, limit: int = 10):
    """
    Get every entity_id of type person from the vector database.
    
    Uses GET method for retrieval operations.
    """
    return "person"

@router.get("/entities/company/")
async def get_company_entities(companyName: str, limit: int = 10):
    """
    Get every entity_id of type company from the vector database.
    
    Uses GET method for retrieval operations.
    """
    return "company"