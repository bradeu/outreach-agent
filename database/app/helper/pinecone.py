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
from datetime import datetime
# from semantic_router.encoders import OpenAIEncoder
# from semantic_chunkers import StatisticalChunker

import logging
logger = logging.getLogger(__name__)

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')

_ = load_dotenv(dotenv_path=env_path)

pinecone_api_key = os.getenv('PINECONE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

pc = Pinecone(api_key=pinecone_api_key)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
open_ai_embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
text_splitter = SemanticChunker(open_ai_embedding, breakpoint_threshold_type="gradient")

class Helper:
    def get_pinecone_index(self, index_name="outreach-agent"):
        """
        Get a Pinecone index instance for health checks or operations.
        
        Args:
            index_name: Name of the Pinecone index
            
        Returns:
            Pinecone index instance
        """
        return pc.Index(index_name)

    async def upsert_method(self, vector_list, namespace, index_name="outreach-agent", entity_type="company"):

        """
        Upsert vectors into Pinecone index.

        Args:
            vector_list: List of vectors to upsert
            index_name: Name of the Pinecone index
            namespace: Namespace for the vectors

        Returns:
            Dictionary containing the upsert operation result
        """

        try:
            index = self.get_pinecone_index(index_name)
            vectors = []
            for v in vector_list:
                vectors.append((str(uuid.uuid4()), v['embedding'], {
                    'entity_id': namespace,
                    'entity_type': entity_type,
                    'sentence': v['sentence'],
                    'created_at': datetime.now().isoformat()
                }))
            
            # return (await index.upsert(
            #     vectors=vectors,
            #     namespace=namespace
            # )).to_dict()
            
            return await asyncio.to_thread(
                lambda: index.upsert(vectors=vectors, namespace=namespace).to_dict()
            )

        except Exception as e:
            raise

    async def query_method(self, vector_list, namespace, limit, index_name="outreach-agent"):

        """
        Query Pinecone index for similar sentences.

        Args:
            vector_list: List of vectors to query
            limit: Number of results to return
            index_name: Name of the Pinecone index
            namespace: Namespace for the vectors

        Returns:
            Dictionary containing the query operation result
        """

        try:
            index = self.get_pinecone_index(index_name)
            result = []
            seen_ids = set()
            for v in vector_list:
                # res = await index.query(
                #     namespace=namespace,
                #     vector=v['embedding'],
                #     top_k=top_k,
                #     include_values=True,
                #     include_metadata=True,
                # )

                logger.info(f"entering index query")

                res = await asyncio.to_thread(
                    lambda: index.query(
                        namespace=namespace,
                        vector=v['embedding'],
                        top_k=limit,
                        include_values=False,
                        include_metadata=True
                    )
                )
                for match in res['matches']:
                    if match['id'] not in seen_ids:
                        result.append({
                            "id": match['id'],
                            "entity_id": match['metadata']['entity_id'],
                            "sentence": match['metadata']['sentence'],
                            "entity_type": match['metadata']['entity_type'],
                            "created_at": match['metadata']['created_at']
                        })
                        seen_ids.add(match['id'])

            logger.info(f"result: {result}")
            return {'similar_sentences': result}
        except Exception as e:
            raise

    async def update_method(self, entity_id, text, index_name="outreach-agent", namespace="ns1"):
        """
        Update a specific entity in the Pinecone index.

        Args:
            entity_id: ID of the entity to update
            text: New text for the entity
            index_name: Name of the Pinecone index
            namespace: Namespace for the vectors

        Returns:
            Dictionary containing the update operation result
        """

        try:
            index = self.get_pinecone_index(index_name)

            json_dict = json.loads(text)

            return await asyncio.to_thread(
                lambda: index.update(id=entity_id, set_metadata=json_dict, namespace=namespace).to_dict()
            )
        except Exception as e:
            raise
    
    async def embed_sentences(self, sentences):
        # embeddings = model.encode(sentences)
        embeddings = await asyncio.to_thread(model.encode, sentences) 
        embed_list = []
        for i in range(len(embeddings)):
            embed_list.append({'embedding' : embeddings[i], 'sentence' : sentences[i]})
        return embed_list

    async def embed_sentences_openai(self, sentences):
        embed_list = []
        for i in range(len(sentences)):
            # embedding = open_ai_embedding.embed_query(sentences[i])
            embedding = await asyncio.to_thread(open_ai_embedding.embed_query, sentences[i])
            embed_list.append({'embedding' : embedding, 'sentence' : sentences[i]})
        return embed_list

    async def split_text_into_sentences(self, text):
        # chunks = chunker(docs=[text]) # don't use this
        # docs = text_splitter.create_documents([text])
        # sentences = []
        # for doc in docs:
        #     sentences.append(doc.page_content)

        # sentences = sent_tokenize(text)
        sentences = await asyncio.to_thread(sent_tokenize, text)
        return sentences
    
db_helper_obj = Helper()