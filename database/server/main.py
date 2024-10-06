from fastapi import FastAPI
from helper import helper_obj
import json

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/query/")
def query_endpoint(text: str, top_k: int, index_name: str, namespace: str):
    sentences = helper_obj.split_text_into_sentences(text)
    vector = helper_obj.embed_sentences(sentences)
    # res = helper_obj.query_method(vector, top_k, index_name, namespace)
    res = helper_obj.query_method(vector)
    return res.to_dict()

@app.post("/upsert/")
def upsert_endpoint(text: str, index_name: str, namespace: str):
    sentences = helper_obj.split_text_into_sentences(text)
    vector = helper_obj.embed_sentences(sentences)
    # res = helper_obj.upsert_method(vector, index_name, namespace)
    res = helper_obj.upsert_method(vector)
    return res.to_dict()