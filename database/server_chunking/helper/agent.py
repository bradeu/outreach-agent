from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from dotenv import load_dotenv

_ = load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:

    def __init__(self, model_query, model_filter, tools, top_k):
        self.system_query = "Decompose the following query into simpler parts"
        graph = StateGraph(AgentState)
        graph.add_node("llm_query", self.call_openai_query)
        graph.add_node("action", self.take_action)
        graph.add_node("llm_filter", self.call_openai_filter)
        graph.add_edge("llm_query", "action")
        graph.add_edge("action", "llm_filter")
        graph.set_entry_point("llm_query")
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model_query = model_query.bind_tools(tools)
        self.model_filter = model_filter.bind_tools(tools)
        self.top_k = top_k

    def exists_action(self, state: AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def call_openai_query(self, state: AgentState):
        messages = state['messages']
        messages = [SystemMessage(content=self.system_query)] + messages
        message = self.model_query.invoke(messages)
        return {'messages': [message]}
    
    def call_openai_filter(self, state: AgentState):
        query = state['messages'][0].content
        system_filter = f"Filter the following results based on the given query:{query}."

        messages = state['messages'][-1]
        messages = [SystemMessage(content=system_filter)] + messages
        message = self.model_filter.invoke(messages)
        return {'messages': [message]}

    def take_action(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f"Calling: {t}")
            if not t['name'] in self.tools:
                print("\n ....bad tool name....")
                result = "bad tool name, retry"
            else:
                result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        print("To the filter model!")
        return {'messages': results}