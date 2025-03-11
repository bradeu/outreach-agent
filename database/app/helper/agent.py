from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Optional, Dict, List
import operator
from langchain_core.messages import AnyMessage, SystemMessage
from dotenv import load_dotenv
import json
from pydantic import BaseModel
import logging
from ast import literal_eval

logger = logging.getLogger("agent_logger")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.propagate = False

_ = load_dotenv()

class QueryResponse(BaseModel):
    sub_queries: List[str]

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:
    def __init__(self, model_query, query_tool, filter_tool):
        graph = StateGraph(AgentState)
        graph.add_node("llm_query", self.call_openai_query)
        graph.add_node("search", self.search) # call it search or rag
        graph.add_node("filter", self.filter)
        graph.add_edge("llm_query", "search")
        graph.add_edge("search", "filter")
        graph.add_edge("filter", END)
        graph.set_entry_point("llm_query")
        self.graph = graph.compile()
        self.model_query = model_query
        self.query_tool = query_tool
        self.filter_tool = filter_tool

    async def call_openai_query(self, state: AgentState):
        messages = state['messages']

        system_query = (
        "Decompose the following query into simpler parts and return the result "
        "as a JSON object with a key 'sub_queries' and a value that is a list of strings. "
        "For example: {\"sub_queries\": [\"Question 1\", \"Question 2\"]}"
        )

        messages = [SystemMessage(content=system_query)] + messages
        message = await self.model_query.with_structured_output(QueryResponse).ainvoke(messages)
        new_state = {'messages': [message]}
        return new_state
    
    async def search(self, state: AgentState):
        logger.info(f"Entering 'search' with state: {state['messages'][-1]}")
        ai_message_content = state['messages'][-1].json()

        try:
            decomposed_queries = json.loads(ai_message_content)
            logger.info(f"decomposed_queries: {decomposed_queries}, with type: {type(decomposed_queries)}")
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON response.")

        logger.info(f"Entering query tool")
        message = await self.query_tool.ainvoke(decomposed_queries)
        logger.info(f"message: {message}")
        new_state = {'messages': [message]}
        return new_state
    
    async def filter(self, state: AgentState):
        logger.info(f"Entering 'filter' with state: {state['messages'][-1].content}")
        db_content = state['messages'][-1].content
        
        try:
            if isinstance(db_content, str):
                decomposed_db_content = literal_eval(db_content)
            else:
                decomposed_db_content = db_content
        except (ValueError, SyntaxError) as e:
            logger.error(f"Error parsing content: {e}")
            logger.debug(f"Problematic content: {db_content}")
            decomposed_db_content = {"results": []}
        
        message = await self.filter_tool.ainvoke(decomposed_db_content)
        new_state = {'messages': [message]}
        return new_state 