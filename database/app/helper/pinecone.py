import os
from dotenv import load_dotenv
from pinecone import Pinecone
import time
import asyncio
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
import uuid
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
# from semantic_router.encoders import OpenAIEncoder
# from semantic_chunkers import StatisticalChunker

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')

_ = load_dotenv(dotenv_path=env_path)

pinecone_api_key = os.getenv('PINECONE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

pc = Pinecone(api_key=pinecone_api_key)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
open_ai_embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
text_splitter = SemanticChunker(open_ai_embedding, breakpoint_threshold_type="gradient")

class Helper:

    async def upsert_method(self, vector_list, index_name="test2", namespace="ns1"):
        try:
            index = pc.Index(index_name)
            vectors = []
            for v in vector_list:
                vectors.append((str(uuid.uuid4()), v['embedding'], {'sentence': v['sentence']}))
            
            return index.upsert(
                vectors=vectors,
                namespace=namespace
            ).to_dict()
        except Exception as e:
            # Log the error if needed
            raise

    async def query_method(self, vector_list, top_k=3, index_name="test2", namespace="ns1"):
        try:
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
                        result.append({
                            "id": match['id'],
                            "sentence": match['metadata']['sentence']
                        })
                        seen_ids.add(match['id'])

            return {'similar_sentences': result}
        except Exception as e:
            # Log the error if needed
            raise
    
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
        # chunks = chunker(docs=[text]) # don't use this
        sentences = sent_tokenize(text)
        # docs = text_splitter.create_documents([text])
        # sentences = []
        # for doc in docs:
        #     sentences.append(doc.page_content)
        return sentences
    
db_helper_obj = Helper()