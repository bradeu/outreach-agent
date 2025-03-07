try:
    from ..helper.pinecone import db_helper_obj
except ImportError:
    from helper.pinecone import db_helper_obj
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
import uuid
import asyncio

@tool
async def query_tool(sub_queries: list) -> ToolMessage:
    """This is a query tool"""

    if not isinstance(sub_queries, list):
        raise ValueError("Expected 'sub_queries' to be a list of strings.")

    res = []
    for sub_query in sub_queries:
        sentences = await db_helper_obj.split_text_into_sentences(sub_query)
        vector = await db_helper_obj.embed_sentences_openai(sentences)
        query_result = await db_helper_obj.query_method(vector)
        res.append(query_result)
    
    tool_call_id = f"tool_call_{uuid.uuid4()}"
    return ToolMessage(name=query_tool.name, content={"results": res}, tool_call_id=tool_call_id)

# print(query_tool.name)
# print(query_tool.description)
# print(query_tool.args)
# print(type(query_tool))