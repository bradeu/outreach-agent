from fastapi import FastAPI, Request
from helper.pinecone import db_helper_obj
from tool.query_tool import query_tool_obj
from inference import inference_obj

app = FastAPI()

@app.get("/")
async def root(request: Request):
    return await request.json()

@app.get("/query/")
async def query_endpoint(request: Request):
    data = await request.json()
    text = data.get("text")
    
    # optimized_query = db_helper_obj.send_to_perplexity(text)

    try:
        top_k = int(data.get("top_k"))
    except:
        top_k = False
    res = inference_obj.query_workflow(text, top_k)

    # sentences = db_helper_obj.split_text_into_sentences(optimized_query)
    # # vector = db_helper_obj.embed_sentences(sentences)
    # vector = db_helper_obj.embed_sentences_openai(sentences)
    # try:
    #     top_k = int(data.get("top_k"))
    #     res = db_helper_obj.query_method(vector, top_k)
    # except:
    #     res = db_helper_obj.query_method(vector)
    # # res = db_helper_obj.query_method(vector, top_k, index_name, namespace)
    return res

@app.post("/upsert/")
async def upsert_endpoint(request: Request):
    data = await request.json()
    text = data.get("text")

    sentences = db_helper_obj.split_text_into_sentences(text)
    # vector = db_helper_obj.embed_sentences(sentences)
    vector = db_helper_obj.embed_sentences_openai(sentences)
    res = db_helper_obj.upsert_method(vector)
    # res = db_helper_obj.upsert_method(vector, index_name, namespace)
    return res