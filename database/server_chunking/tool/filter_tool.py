from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
import uuid

@tool
def filter_tool(results: list) -> ToolMessage:
    """This is a filter tool"""

    if not isinstance(results, list):
        raise ValueError("Expected 'results' to be a list of json.")
    
    