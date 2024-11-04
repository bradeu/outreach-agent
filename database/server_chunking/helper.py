import os
from dotenv import load_dotenv
from pinecone import Pinecone
import time
# from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
import uuid
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
import requests
# from semantic_router.encoders import OpenAIEncoder
# from semantic_chunkers import StatisticalChunker


load_dotenv()

pinecone_api_key = os.getenv('PINECONE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')

pc = Pinecone(api_key=pinecone_api_key)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
open_ai_embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
text_splitter = SemanticChunker(open_ai_embedding, breakpoint_threshold_type="gradient")

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
        ).to_dict()

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

        return {'similar_sentences' : result}
    
    def embed_sentences(self, sentences):
        embeddings = model.encode(sentences)
        embed_list = []
        for i in range(len(embeddings)):
            embed_list.append({'embedding' : embeddings[i], 'sentence' : sentences[i]})
        return embed_list

    def split_text_into_sentences(self, text):
        # chunks = chunker(docs=[text])
        # sentences = sent_tokenize(text)
        docs = text_splitter.create_documents([text])
        sentences = []
        for doc in docs:
            sentences.append(doc.page_content)
        return sentences

    def send_to_perplexity(self, user_query):
        headers = {
            "Authorization": f"Bearer {perplexity_api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get("https://api.perplexity.ai/search", headers=headers, params={"query": user_query})
        perplexity_data = response.json()
        real_time_answer = perplexity_data.get("answer")
        return real_time_answer
    
helper_obj = Helper()