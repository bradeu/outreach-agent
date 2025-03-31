from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
import uuid
import asyncio

@tool
async def filter_tool(results: list) -> ToolMessage:
    """This is a filter tool"""

    if not isinstance(results, list):
        raise ValueError("Expected 'results' to be a list of json.")
    
    seen_ids = set()
    res = []
    
    for similar_sentences_json in results:
        for sentences in similar_sentences_json['similar_sentences']:
            if sentences['id'] not in seen_ids:
                res.append(
                    { 
                        "entity_id": sentences['entity_id'],
                        "sentence": sentences['sentence'],
                        "entity_type": sentences['entity_type'],
                        "created_at": sentences['created_at']
                    }
                )
                seen_ids.add(sentences['id'])
    
    tool_call_id = f"tool_call_{uuid.uuid4()}"
    return ToolMessage(name=filter_tool.name, content={"results": res}, tool_call_id=tool_call_id) 