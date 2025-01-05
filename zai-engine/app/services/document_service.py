from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import UploadFile, HTTPException
from bson import ObjectId
from elasticsearch import AsyncElasticsearch, Elasticsearch
import shutil
import os
import logging
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from app.core.database import db
from app.models.document import Document, DocumentChunk
from app.utils.file_utils import get_storage_path, save_upload_file
from config import config

class DocumentService:
    def __init__(self):
        """Initialize document service."""
        self.db: AsyncIOMotorDatabase = None
        self.es: AsyncElasticsearch = None
        
        # Initialize embeddings with the new v0.3 format
        self.embeddings = OpenAIEmbeddings(
            api_key=config["openai"]["api_key"],
            model="text-embedding-ada-002",
            dimensions=1536,
            show_progress_bar=True
        )

    async def connect(self):
        """Establish database connections."""
        if self.db is None:
            await db.connect()
            self.db = db.get_database()
        
        if self.es is None:
            self.es = AsyncElasticsearch(
                hosts=[config["elasticsearch"]["connection"]["url"]],
                basic_auth=(
                    config["elasticsearch"]["connection"]["user"],
                    config["elasticsearch"]["connection"]["password"]
                )
            )

    async def close(self):
        """Close database connections."""
        if self.db is not None:
            await db.close()
            self.db = None
        
        if self.es is not None:
            await self.es.close()
            self.es = None

    async def create_es_index(self):
        """Create Elasticsearch index with proper mapping for embeddings."""
        await self.connect()
        
        mapping = {
            "mappings": {
                "properties": {
                    "chunk_id": {"type": "keyword"},
                    "document_id": {"type": "keyword"},
                    "content": {"type": "text"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 1536,  # OpenAI ada-002 embedding dimensions
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
        
        try:
            await self.es.indices.create(
                index=f"{config['elasticsearch']['index']['prefix']}_chunks",
                body=mapping,
                ignore=400  # ignore 400 already exists error
            )
        except Exception as e:
            logging.error(f"Failed to create Elasticsearch index: {str(e)}")
            raise

    async def create_document(self, file: UploadFile) -> Document:
        """Create initial document entry."""
        await self.connect()
        
        try:
            # Validate file extension
            if not any(file.filename.lower().endswith(ext) for ext in config["storage"]["limits"]["allowed_extensions"]):
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed. Allowed types: {config['storage']['limits']['allowed_extensions']}"
                )
            
            # Save file to uploads directory
            upload_path = get_storage_path(config["storage"]["directories"]["upload"])
            file_path, mime_type = await save_upload_file(file, upload_path)
            
            # Create document record with a new ObjectId
            doc_id = ObjectId()
            document = Document(
                id=doc_id,
                filename=file.filename,
                file_path=file_path,
                mime_type=mime_type,
                status="pending"
            )
            
            # Save initial document record
            await self.db.documents.insert_one(document.dict(by_alias=True))
            return document

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create document: {str(e)}"
            )

    async def list_documents(self) -> list[Document]:
        """List all documents."""
        await self.connect()
        cursor = self.db.documents.find()
        documents = []
        async for doc in cursor:
            documents.append(Document(**doc))
        return documents
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by ID."""
        await self.connect()
        doc = await self.db.documents.find_one({"_id": ObjectId(document_id)})
        return Document.parse_obj(doc) if doc else None
    
    async def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Retrieve all chunks for a document."""
        await self.connect()
        cursor = self.db.document_chunks.find({"document_id": document_id})
        chunks = await cursor.to_list(length=None)
        return [DocumentChunk.parse_obj(chunk) for chunk in chunks]

    async def semantic_search(self, query: str, limit: int = 5) -> List[dict]:
        """Perform semantic search using embeddings."""
        await self.connect()
        
        try:
            # Generate embedding for the query
            query_embedding = await self.embeddings.aembed_query(query)
            
            # Prepare the search query
            search_query = {
                "size": limit,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": query_embedding}
                        }
                    }
                }
            }
            
            # Execute search
            results = await self.es.search(
                index=f"{config['elasticsearch']['index']['prefix']}_chunks",
                body=search_query
            )
            
            # Process results
            hits = []
            for hit in results["hits"]["hits"]:
                source = hit["_source"]
                hits.append({
                    "chunk_id": source["chunk_id"],
                    "document_id": source["document_id"],
                    "content": source["content"],
                    "metadata": source["metadata"],
                    "score": hit["_score"]
                })
            
            return hits
            
        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to perform search: {str(e)}"
            ) 