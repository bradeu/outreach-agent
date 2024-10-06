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
    def upsert_method(self, vector_list, index_name="test1", namespace="ns1"):
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)

        index = pc.Index(index_name)

        vectors = []
        for v in vector_list:
            vectors.append((str(uuid.uuid4()), v['embedding'], {'sentence' : v['sentence']}))

        return index.upsert(
            vectors=vectors,
            namespace=namespace
        )

    def query_method(self, vector_list, top_k=10, index_name="test1", namespace="ns1"):
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)

        index = pc.Index(index_name)

        result = []
        seen_ids = set()
        for v in vector_list:
            res = index.query(
                namespace=namespace,
                vector=v['embedding'].tolist(),
                top_k=top_k,
                include_values=True,
                include_metadata=True,
            )

            for match in res['matches']:
                if match['id'] not in seen_ids:
                    result.append(match['metadata']['sentence'])
                    seen_ids.add(match['id'])

        return result
    
    def embed_sentences(self, sentences):
        embeddings = model.encode(sentences)
        embed_list = []
        for i in range(len(embeddings)):
            embed_list.append({'embedding' : embeddings[i], 'sentence' : sentences[i]})
        return embed_list

    def split_text_into_sentences(self, text):
        sentences = sent_tokenize(text)
        return sentences
    
helper_obj = Helper()