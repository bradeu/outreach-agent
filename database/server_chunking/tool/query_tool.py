from helper.pinecone import db_helper_obj
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

@tool
def query_tool(self, args: dict) -> ToolMessage:
    sub_queries = args.get("sub_queries", [])
    top_k = args.get("top_k", None)

    if not isinstance(sub_queries, list):
        raise ValueError("Expected 'sub_queries' to be a list of strings.")
    
    res = []
    for sub_query in sub_queries:
        sentences = db_helper_obj.split_text_into_sentences(sub_query)
        vector = db_helper_obj.embed_sentences_openai(sentences)

        if top_k:
            res.append(db_helper_obj.query_method(vector, top_k))
        else:
            res.append(db_helper_obj.query_method(vector))
    
    return ToolMessage(name=self.name, content={"results": res})

# print(query_tool.name)
# print(query_tool.description)
# print(query_tool.args)
# print(type(query_tool))
