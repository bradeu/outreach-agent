from langchain_openai import ChatOpenAI
from database.server_chunking.helper.agent import Agent
from langchain_core.messages import HumanMessage
from tool.query_tool import query_tool_obj

class Inference:

    def query_workflow(user_query, top_k):
        tool = query_tool_obj
        model = ChatOpenAI(model="gpt-3.5-turbo") #change to 4.0 mini
        abot = Agent(model, model, [tool], top_k)

        messages = [HumanMessage(content=user_query)]
        result = abot.graph.invoke({"messages": messages})
        return result['messages'][-1].content
    
inference_obj = Inference()