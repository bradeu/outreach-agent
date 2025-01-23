from fastapi import FastAPI, Request
from app.helper.pinecone import db_helper_obj
from app.inference import inference_obj
import time
from fastapi.middleware.cors import CORSMiddleware
import atexit
import multiprocessing
import multiprocessing.resource_tracker as resource_tracker
import signal

app = FastAPI()

@app.get("/")
async def root(request: Request):
	return await request.json()

@app.get("/query/")
async def query_endpoint(request: Request):
	data = await request.json()
	text = data.get("text")
	
	# optimized_query = db_helper_obj.send_to_perplexity(text)

	# try:
	#     top_k = int(data.get("top_k"))
	# except:
	#     top_k = False
	# res = inference_obj.query_workflow(text, top_k)
	
	start_time = time.time()
	res = inference_obj.query_workflow(text)
	end_time = time.time()
	execution_time = end_time - start_time
	print(f"Execution time: {execution_time} seconds")

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

def cleanup():
    """Cleanup function to handle graceful shutdown"""
	try:
        if resource_tracker._resource_tracker:
            resource_tracker._resource_tracker._stop()
            
        resource_tracker._resource_tracker = None
        resource_tracker._pid = None
        
        multiprocessing.current_process()._config['semprefix'] = '/mp'
        
    except (FileNotFoundError, AttributeError, Exception) as e:
        print(f"Cleanup warning (safe to ignore): {e}")
    
    try:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
    except Exception as e:
        print(f"Signal handling warning: {e}")

atexit.register(cleanup)

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        cleanup()