from fastapi import FastAPI, Request
from helper import helper_obj

app = FastAPI()

@app.get("/")
async def root(request: Request):
    return await request.json()

@app.get("/query/")
async def query_endpoint(request: Request):
    data = await request.json()
    text = data.get("text")
    
    optimized_query = helper_obj.send_to_perplexity(text)
    sentences = helper_obj.split_text_into_sentences(optimized_query)
    # vector = helper_obj.embed_sentences(sentences)
    vector = helper_obj.embed_sentences_openai(sentences)
    try:
        top_k = int(data.get("top_k"))
        res = helper_obj.query_method(vector, top_k)
    except:
        res = helper_obj.query_method(vector)
    # res = helper_obj.query_method(vector, top_k, index_name, namespace)
    return res

@app.post("/upsert/")
async def upsert_endpoint(request: Request):
    data = await request.json()
    text = data.get("text")

    sentences = helper_obj.split_text_into_sentences(text)
    # vector = helper_obj.embed_sentences(sentences)
    vector = helper_obj.embed_sentences_openai(sentences)
    res = helper_obj.upsert_method(vector)
    # res = helper_obj.upsert_method(vector, index_name, namespace)
    return res