from typing import Dict, List, Optional
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack_integrations.components.retrievers.elasticsearch import ElasticsearchEmbeddingRetriever
from haystack.components.generators.openai import OpenAIGenerator
from haystack.dataclasses import Document
from haystack.utils import Secret
from elasticsearch import AsyncElasticsearch
import os

from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.core.database import db
from config import config

class RAGService:
    """Service for RAG (Retrieval Augmented Generation) using Haystack 2.x."""
    
    def __init__(self):
        """Initialize RAG service."""
        self.llm_service = LLMService()
        self.embedding_service = EmbeddingService()
        self.document_store = None
        self.retriever = None
        self.generator = None
        self.current_llm_id = None
        self.prompt_template = """Answer the question based on the given context. If you cannot find 
        the answer in the context, say "I cannot answer this question based on the provided context." 
        Do not make up any information.
        
        Context: {documents}
        
        Question: {query}
        
        Answer: """

    async def initialize(self, llm_id: str):
        """Initialize RAG components with specified LLM."""
        # Get LLM provider from MongoDB
        provider = await self.llm_service.get_provider(llm_id)
        if not provider:
            raise ValueError(f"Failed to initialize LLM provider: {llm_id}")
        
        # Initialize embedding service
        await self.embedding_service.initialize()
        
        # Initialize Elasticsearch document store if not already done
        if not self.document_store:
            # Create Elasticsearch client
            es_client = AsyncElasticsearch(
                hosts=[config["elasticsearch"]["connection"]["url"]],
                basic_auth=(
                    config["elasticsearch"]["connection"]["user"],
                    config["elasticsearch"]["connection"]["password"]
                )
            )
            
            # Create index with proper mapping if it doesn't exist
            index_name = f"{config['elasticsearch']['index']['prefix']}_chunks"
            if not await es_client.indices.exists(index=index_name):
                mapping = {
                    "mappings": {
                        "properties": {
                            "chunk_id": {"type": "keyword"},
                            "document_id": {"type": "keyword"},
                            "content": {"type": "text"},
                            "embedding": {
                                "type": "dense_vector",
                                "dims": self.embedding_service.embedding_dim,
                                "index": True,
                                "similarity": "cosine"
                            },
                            "metadata": {
                                "properties": {
                                    "filename": {"type": "keyword"},
                                    "mime_type": {"type": "keyword"},
                                    "section_number": {"type": "integer"},
                                    "page_number": {"type": "integer"}
                                }
                            }
                        }
                    },
                    "settings": {
                        "number_of_shards": config["elasticsearch"]["index"]["shards"],
                        "number_of_replicas": config["elasticsearch"]["index"]["replicas"],
                        "refresh_interval": config["elasticsearch"]["index"]["refresh_interval"]
                    }
                }
                await es_client.indices.create(index=index_name, body=mapping)
            
            # Initialize document store with the prepared index
            self.document_store = ElasticsearchDocumentStore(
                hosts=[config["elasticsearch"]["connection"]["url"]],
                basic_auth=(
                    config["elasticsearch"]["connection"]["user"],
                    config["elasticsearch"]["connection"]["password"]
                ),
                index=index_name
            )
            await es_client.close()
        
        # Initialize retriever with Elasticsearch
        self.retriever = ElasticsearchEmbeddingRetriever(
            document_store=self.document_store,
            top_k=5
        )
        
        # Initialize generator with the dynamic LLM
        self.generator = OpenAIGenerator(
            api_key=Secret.from_token(provider.api_key),
            model=provider.model_name,
            generation_kwargs={
                "max_tokens": provider.max_tokens,
                "temperature": provider.temperature
            }
        )
        
        # Store current LLM ID
        self.current_llm_id = llm_id

    async def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the document store."""
        if not self.document_store:
            raise RuntimeError("Document store not initialized. Call initialize() first.")
        
        # Write documents to store
        self.document_store.write_documents(documents)

    async def query(self, query: str, **kwargs) -> Dict:
        """Execute RAG query pipeline."""
        if not self.retriever or not self.generator:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        try:
            # Set retriever parameters
            self.retriever.top_k = kwargs.get("top_k", 5)
            
            # Generate query embedding using the embedding service
            query_embedding = await self.embedding_service.get_embedding(query)
            
            # Run retriever with the embedding
            retrieved_docs = self.retriever.run(
                query_embedding=query_embedding
            )
            
            # Build prompt with retrieved documents
            prompt = self.prompt_template.format(
                documents="\n".join([doc.content for doc in retrieved_docs["documents"]]),
                query=query
            )
            
            # Generate answer using the prompt
            answer = self.generator.run(prompt=prompt)
            print(f"OpenAI Generator Response: {answer}")  # Debug print
            
            # Process documents for response
            documents = [
                {
                    "content": doc.content,
                    "score": doc.score if hasattr(doc, "score") else None,
                    "meta": doc.meta
                }
                for doc in retrieved_docs["documents"]
            ]
            
            return {
                "answer": answer["replies"][0],  # OpenAIGenerator returns {'replies': [...]}
                "documents": documents,
                "query": query,
                "llm_id": self.current_llm_id
            }
            
        except Exception as e:
            raise RuntimeError(f"RAG pipeline error: {str(e)}")

    def update_prompt_template(self, template: str):
        """Update the prompt template used by the RAG pipeline."""
        self.prompt_template = template 