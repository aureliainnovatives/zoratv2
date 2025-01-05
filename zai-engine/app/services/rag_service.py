from typing import Dict, List, Optional
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack_integrations.components.retrievers.elasticsearch import ElasticsearchEmbeddingRetriever
from haystack.components.generators.openai import OpenAIGenerator
from haystack.components.embedders import OpenAITextEmbedder
from haystack.dataclasses import Document
from haystack.utils import Secret
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from elasticsearch import AsyncElasticsearch
import os

from app.services.llm_service import LLMService
from app.core.database import db
from config import config

class RAGService:
    """Service for RAG (Retrieval Augmented Generation) using Haystack 2.x."""
    
    def __init__(self):
        """Initialize RAG service."""
        self.llm_service = LLMService()
        self.document_store = None
        self.pipeline = None
        self.current_llm_id = None
        self.prompt_template = """Answer the question based on the given context. If you cannot find 
        the answer in the context, say "I cannot answer this question based on the provided context." 
        Do not make up any information.

        Context:
        {% for document in documents %}
            {{ document.content }}
        {% endfor %}

        Question: {{ query }}

        Answer: """

    async def initialize(self, llm_id: str):
        """Initialize RAG components with specified LLM."""
        # Get LLM provider from MongoDB
        provider = await self.llm_service.get_provider(llm_id)
        if not provider:
            raise ValueError(f"Failed to initialize LLM provider: {llm_id}")
        
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
                                "dims": 1536,  # OpenAI ada-002 dimension
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
        
        # Initialize Haystack Pipeline components
        embedder = OpenAITextEmbedder(
            api_key=Secret.from_token(config["openai"]["api_key"]),
            model="text-embedding-ada-002"
        )
        
        retriever = ElasticsearchEmbeddingRetriever(
            document_store=self.document_store,
            top_k=5
        )
        
        prompt_builder = PromptBuilder(template=self.prompt_template)
        
        generator = OpenAIGenerator(
            api_key=Secret.from_token(provider.api_key),
            model=provider.model_name,
            generation_kwargs={
                "max_tokens": provider.max_tokens,
                "temperature": provider.temperature
            }
        )
        
        # Create and configure the pipeline
        self.pipeline = Pipeline()
        self.pipeline.add_component("embedder", embedder)
        self.pipeline.add_component("retriever", retriever)
        self.pipeline.add_component("prompt_builder", prompt_builder)
        self.pipeline.add_component("generator", generator)
        
        # Connect components in the pipeline
        self.pipeline.connect("embedder.embedding", "retriever.query_embedding")
        self.pipeline.connect("retriever.documents", "prompt_builder.documents")
        self.pipeline.connect("prompt_builder", "generator")
        
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
        if not self.pipeline:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        try:
            # Update retriever's top_k if provided
            if "top_k" in kwargs:
                self.pipeline.get_component("retriever").top_k = kwargs["top_k"]
            
            # Run the pipeline
            result = self.pipeline.run({
                "embedder": {"text": query},
                "prompt_builder": {"query": query}
            })
            
            # Process documents for response
            documents = [
                {
                    "content": doc.content,
                    "score": doc.score if hasattr(doc, "score") else None,
                    "meta": doc.meta
                }
                for doc in result["retriever"]["documents"]
            ]
            
            return {
                "answer": result["generator"]["replies"][0],
                "documents": documents,
                "query": query,
                "llm_id": self.current_llm_id
            }
            
        except Exception as e:
            raise RuntimeError(f"RAG pipeline error: {str(e)}")

    def update_prompt_template(self, template: str):
        """Update the prompt template used by the RAG pipeline."""
        if self.pipeline:
            prompt_builder = self.pipeline.get_component("prompt_builder")
            prompt_builder.template = template
        self.prompt_template = template 