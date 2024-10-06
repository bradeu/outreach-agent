import os
from dotenv import load_dotenv
from pinecone import Pinecone
import time
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
import uuid

load_dotenv()

api_key = os.getenv('API_KEY')
pc = Pinecone(api_key=api_key)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

class Helper:
    def upsert_method(self, vector, index_name="test1", namespace="ns1"):
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)

        index = pc.Index(index_name)

        vectors = []
        for v in vector:
            vectors.append((str(uuid.uuid4()), v))

        return index.upsert(
            vectors=vectors,
            namespace=namespace
        )

    def query_method(self, vector, index_name="test1", namespace="ns1"):
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)

        index = pc.Index(index_name)

        return index.query(
            namespace=namespace,
            vector=vector,
            include_values=True,
            include_metadata=True,
        )
    
    def embed_sentences(self, sentences):
        embeddings = model.encode(sentences)
        return embeddings

    def split_text_into_sentences(self, text):
        sentences = sent_tokenize(text)
        return sentences
    
helper_obj = Helper()