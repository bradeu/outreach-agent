from fastapi import FastAPI, Request
try:
    from .helper.pinecone import db_helper_obj
    from .inference import inference_obj
except ImportError:
    from helper.pinecone import db_helper_obj
    from inference import inference_obj
import time
# from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.get("/")
async def root(request: Request):
    return await request.json()

@app.get("/query/")
async def query_endpoint(request: Request):
    data = await request.json()
    text = data.get("text")
    
    start_time = time.time()
    res = await inference_obj.query_workflow(text)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

    return res

@app.post("/upsert/")
async def upsert_endpoint(request: Request):
    data = await request.json()
    text = data.get("text")

    start_time = time.time()
    sentences = db_helper_obj.split_text_into_sentences(text)
    vector = db_helper_obj.embed_sentences_openai(sentences)
    res = await db_helper_obj.upsert_method(vector)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

    return res