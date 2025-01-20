from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Optional, Dict, List
import operator
from langchain_core.messages import AnyMessage, SystemMessage
from dotenv import load_dotenv
import json
from pydantic import BaseModel
import logging

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

    def call_openai_query(self, state: AgentState):
        messages = state['messages']

        system_query = (
        "Decompose the following query into simpler parts and return the result "
        "as a JSON object with a key 'sub_queries' and a value that is a list of strings. "
        "For example: {\"sub_queries\": [\"Question 1\", \"Question 2\"]}"
        )

        messages = [SystemMessage(content=system_query)] + messages
        message = self.model_query.with_structured_output(QueryResponse).invoke(messages)
        new_state = {'messages': [message]}
        return new_state
    
    def search(self, state: AgentState):
        logger.info(f"Entering 'search' with state: {state['messages'][-1]}")
        ai_message_content = state['messages'][-1].json()

        try:
            decomposed_queries = json.loads(ai_message_content)
            logger.info(f"decomposed_queries: {decomposed_queries}")
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON response.")

        message = self.query_tool.invoke(decomposed_queries)
        new_state = {'messages': [message]}
        return new_state
    
    def filter(self, state: AgentState):
        logger.info(f"Entering 'filter' with state: {state['messages'][-1].content}")
        db_content = state['messages'][-1].content
        decomposed_db_content = {"results":[]}

        try:
            valid_json = db_content.replace('"s', "'s").replace('\"', '"')
            logger.info(f"valid_json: {valid_json}")
            decomposed_db_content = json.loads(valid_json)
            # logger.info(f"decomposed_db_content: {decomposed_db_content}")
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON response.")
        
        message = self.filter_tool.invoke(decomposed_db_content)
        new_state = {'messages': [message]}
        return new_state