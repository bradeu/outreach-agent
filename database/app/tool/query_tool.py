try:
    from ..helper.pinecone import db_helper_obj
    from ..helper.namespace import get_namespace    
except ImportError:
    from helper.pinecone import db_helper_obj
    from helper.namespace import get_namespace
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
import uuid
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

@tool
async def query_tool(sub_queries: list) -> ToolMessage:
    """This is a query tool"""

    logger.info(f"Entering query tool inside tool")
    if not isinstance(sub_queries, list):
        raise ValueError("Expected 'sub_queries' to be a list of strings.")

    namespace = get_namespace()
    logger.info(f"namespace: {namespace}")
    res = []
    for sub_query in sub_queries:
        sentences = await db_helper_obj.split_text_into_sentences(sub_query)
        vector = await db_helper_obj.embed_sentences_openai(sentences)
        logger.info(f"entering query_method")
        query_result = await db_helper_obj.query_method(vector, namespace)
        logger.info(f"query_result: {query_result}")
        res.append(query_result)
    
    tool_call_id = f"tool_call_{uuid.uuid4()}"
    return ToolMessage(name=query_tool.name, content={"results": res}, tool_call_id=tool_call_id)

# print(query_tool.name)
# print(query_tool.description)
# print(query_tool.args)
# print(type(query_tool))