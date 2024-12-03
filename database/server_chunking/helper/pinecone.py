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

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')

_ = load_dotenv(dotenv_path=env_path)

pinecone_api_key = os.getenv('PINECONE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')

pc = Pinecone(api_key=pinecone_api_key)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
open_ai_embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
text_splitter = SemanticChunker(open_ai_embedding, breakpoint_threshold_type="gradient")

class Helper:
    def upsert_method(self, vector_list, index_name="test2", namespace="ns1"):
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

    def query_method(self, vector_list, top_k=10, index_name="test2", namespace="ns1"):
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)

        index = pc.Index(index_name)

        result = []
        seen_ids = set()
        for v in vector_list:
            res = index.query(
                namespace=namespace,
                vector=v['embedding'],
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

    def embed_sentences_openai(self, sentences):
        embed_list = []
        for i in range(len(sentences)):
            embedding = open_ai_embedding.embed_query(sentences[i])
            embed_list.append({'embedding' : embedding, 'sentence' : sentences[i]})
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
        url = "https://api.perplexity.ai/chat/completions"

        system_content = (
            "Your task is to improve the following user queries to make them more effective for "
            "searching in a vector database using OpenAIEmbeddings with a vector dimension of 1536.\n\n"
            "Instructions:\n"
            "- Rewrite the query to include related terms if they improve relevance.\n"
            "- Resolve any ambiguous terms to make the query more specific.\n"
            "- Focus on key concepts related to the user's intent.\n\n"
            "Return only the optimized query. Do not provide an answer to the question."
        )

        payload = {
            "model": "llama-3.1-sonar-small-128k-chat",
            "messages": [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            "max_tokens": 200,
        }
        headers = {
            "Authorization": f"Bearer {perplexity_api_key}",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        perplexity_data = response.json()
        return perplexity_data['choices'][0].get('message').get('content')
    
db_helper_obj = Helper()