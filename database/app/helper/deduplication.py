try:
    from ..helper.pinecone import db_helper_obj
except ImportError:
    from helper.pinecone import db_helper_obj

from langchain_openai import ChatOpenAI
from pydantic import BaseModel
import logging
logger = logging.getLogger(__name__)

class DeduplicationResponse(BaseModel):
    entity_id: str

class Deduplication:
    def __init__(self):
        self.deduplication_model = ChatOpenAI(model="gpt-4o-mini")

    async def get_entity_ids(self):
        index = await db_helper_obj.get_pinecone_index()
        stats = index.describe_index_stats()
        entity_ids = list(stats["namespaces"].keys())
        return entity_ids

    async def deduplicate_entity_id(self, entity_id):
        # query = f"""
        # You are a deduplication agent, here is the new entity_id: {entity_id}, 
        # here is the available list of entity_ids: {self.get_entity_ids()}, 
        # If the new query is not so different semantically with one of the entity_ids from the list, 
        # please return the entity_id from the list. If not, please return a new entity_id.
        # """

        query = f"""
        You are a deduplication agent, here is the new entity_id: {entity_id}, 
        here is the available list of entity_ids: {await self.get_entity_ids()}.
        Please return just the entity_id in the list that is most similar to the new entity_id.
        """
        logger.info(f"Entering deduplication with query: {query}")
        response = await self.deduplication_model.with_structured_output(DeduplicationResponse).ainvoke(query)
        logger.info(f"Deduplication response: {response}")
        logger.info(f"Deduplication response type: {type(response)}")
        return response.entity_id

deduplication_obj = Deduplication()
