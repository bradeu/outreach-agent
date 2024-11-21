from helper.pinecone import db_helper_obj

class QueryTool:
    def invoke(self, sub_queries, top_k):
        res = []

        for sub_query in sub_queries:
            sentences = db_helper_obj.split_text_into_sentences(sub_query)
            vector = db_helper_obj.embed_sentences_openai(sentences)

            if top_k != 0:
                res.append(db_helper_obj.query_method(vector, top_k))
            else:
                res.append(db_helper_obj.query_method(vector))
        
        return res
    
query_tool_obj = QueryTool()