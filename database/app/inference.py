from langchain_openai import ChatOpenAI
from app.helper.agent import Agent
from langchain_core.messages import HumanMessage
from app.tool.query_tool import query_tool
from app.tool.filter_tool import filter_tool

class Inference:
    async def query_workflow(self, user_query):
        query = query_tool
        filter = filter_tool
        model = ChatOpenAI(model="gpt-4o-mini")  # Updated to GPT-4o-mini
        abot = Agent(model, query, filter)

        messages = [HumanMessage(content=user_query)]
        result = await abot.graph.ainvoke({"messages": messages})
        return result['messages'][-1].content
    
inference_obj = Inference() 