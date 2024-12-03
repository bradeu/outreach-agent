from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage
from dotenv import load_dotenv
import json

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


_ = load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:
    def __init__(self, model_query, tool):
        graph = StateGraph(AgentState)
        graph.add_node("llm_query", self.call_openai_query)
        graph.add_node("search", self.search) # call it search or rag
        # graph.add_node("llm_filter", self.call_openai_filter)
        graph.add_edge("llm_query", "search")
        # graph.add_edge("search", "llm_filter")
        graph.add_edge("search", END)
        graph.set_entry_point("llm_query")
        self.graph = graph.compile()
        # self.tools = {t.name: t for t in tools}
        # self.model_query = model_query.bind_tools(tools)
        self.model_query = model_query
        # self.model_filter = model_filter
        self.tool = tool

    def call_openai_query(self, state: AgentState):
        logging.debug(f"Entering 'call_openai_query' with state: {state}")
        messages = state['messages']
        # system_query = "Decompose the following query into simpler parts"

        system_query = (
        "Decompose the following query into simpler parts and return the result "
        "as a JSON object with a key 'sub_queries' and a value that is a list of strings. "
        "For example: {\"sub_queries\": [\"Question 1\", \"Question 2\"]}"
        )

        messages = [SystemMessage(content=system_query)] + messages
        message = self.model_query.invoke(messages)
        new_state = {'messages': [message]}
        logging.debug(f"Exiting 'call_openai_query' with new state: {new_state}")
        return new_state
    
    def search(self, state: AgentState):
        logging.debug(f"Entering 'search' with state: {state}")
        ai_message_content = state['messages'][-1].content

        try:
            decomposed_queries = json.loads(ai_message_content)
            logging.debug(f"decomposed_queries: {decomposed_queries}")
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON response.")

        message = self.tool.invoke(decomposed_queries)
        new_state = {'messages': [message]}
        logging.debug(f"Exiting 'search' with new state: {new_state}")
        return new_state
    
    # def call_openai_filter(self, state: AgentState):
    #     query = state['messages'][0].content
    #     system_filter = f"Filter and summarize the following results based on the given query:{query}."

    #     messages = state['messages'][-1]
    #     messages = [SystemMessage(content=system_filter)] + messages
    #     message = self.model_filter.invoke(messages)
    #     return {'messages': [message]}

    # def exists_action(self, state: AgentState):
    #     result = state['messages'][-1]
    #     return len(result.tool_calls) > 0

    # def take_action(self, state: AgentState):
    #     tool_calls = state['messages'][-1].tool_calls
    #     results = []
    #     for t in tool_calls:
    #         print(f"Calling: {t}")
    #         if not t['name'] in self.tools:
    #             print("\n ....bad tool name....")
    #             result = "bad tool name, retry"
    #         else:
    #             result = self.tools[t['name']].invoke(t['args'])
    #         results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
    #     print("To the filter model!")
    #     return {'messages': results}