import asyncio
import logging
from datetime import datetime
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from docling.document_converter import DocumentConverter
from langchain_openai import OpenAIEmbeddings
from bson import ObjectId
from elasticsearch import AsyncElasticsearch
import os
import shutil
import time
import traceback

from app.models.document import Document, DocumentChunk, DocumentMetadata, ContentStats, ChunkingStrategy
from app.services.document_analysis import DocumentAnalyzer, SmartChunker
from app.utils.file_utils import get_storage_path
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        """Initialize document processor."""
        self.mongo_client = AsyncIOMotorClient(
            config["mongodb"]["connection"]["url"],
            maxPoolSize=config["mongodb"]["connection"]["max_connections"],
            minPoolSize=config["mongodb"]["connection"]["min_connections"],
            serverSelectionTimeoutMS=config["mongodb"]["options"]["timeout_ms"],
            retryWrites=config["mongodb"]["options"]["retry_writes"]
        )
        self.db = self.mongo_client[config["mongodb"]["connection"]["db_name"]]
        self.es = AsyncElasticsearch(
            hosts=[config["elasticsearch"]["connection"]["url"]],
            basic_auth=(
                config["elasticsearch"]["connection"]["user"],
                config["elasticsearch"]["connection"]["password"]
            )
        )
        
        # Initialize components
        self.parser = DocumentConverter()
        self.analyzer = DocumentAnalyzer()
        self.chunker = SmartChunker(self.analyzer)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config["openai"]["api_key"],
            model=config["openai"]["model"]
        )

    async def close(self):
        """Close connections."""
        await self.es.close()
        self.mongo_client.close()

    async def process_document(self, doc_id: str):
        """Process a single document with enhanced analysis."""
        try:
            # Get document
            doc = await self.db.documents.find_one({"_id": ObjectId(doc_id)})
            if not doc:
                logger.error(f"Document {doc_id} not found")
                return

            # Update status to parsing
            await self.db.documents.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": {"status": "parsing"}}
            )

            # Start timer for processing
            start_time = time.time()
            
            # Parse document using docling
            try:
                logger.info(f"Starting to parse document: {doc['file_path']}")
                result = self.parser.convert(doc["file_path"])
                logger.info(f"Successfully parsed document. Found {len(result.pages)} pages.")
                
            except Exception as e:
                logger.error(f"Error parsing document: {str(e)}")
                logger.error(traceback.format_exc())
                raise
            
            # Extract text content and analyze document structure
            doc_content = ""
            section_structure = []
            current_section = None
            
            for page_num, page in enumerate(result.pages, 1):
                page_text = []
                for cell in page.cells:
                    if hasattr(cell, 'text') and cell.text:
                        page_text.append(cell.text)
                        
                        # Check for section headers
                        section_type, level = self.analyzer.identify_section_type(cell.text)
                        if section_type == 'heading':
                            if current_section:
                                current_section['end_page'] = page_num - 1
                                section_structure.append(current_section)
                            current_section = {
                                'title': cell.text.strip(),
                                'level': level,
                                'start_page': page_num
                            }
                
                doc_content += "\n".join(page_text) + "\n\n"
            
            # Add final section if exists
            if current_section:
                current_section['end_page'] = len(result.pages)
                section_structure.append(current_section)

            logger.info(f"Extracted {len(doc_content)} characters of text content")

            # Extract document metadata
            doc_metadata = self.analyzer.extract_metadata(doc_content)
            
            # Create intelligent chunks
            chunks = self.chunker.create_chunks(doc_content, doc_id)
            logger.info(f"Created {len(chunks)} intelligent chunks")

            # Move file to processed directory
            processed_path = get_storage_path(config["storage"]["directories"]["processed"])
            processed_file = os.path.join(processed_path, os.path.basename(doc["file_path"]))
            shutil.move(doc["file_path"], processed_file)

            # Update status to generating embeddings
            await self.db.documents.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": {"status": "generating_embeddings"}}
            )

            try:
                logger.info("Generating embeddings...")
                chunk_contents = [chunk['content'] for chunk in chunks]
                embeddings_list = await self.embeddings.aembed_documents(chunk_contents)
                logger.info(f"Generated {len(embeddings_list)} embeddings")
            except Exception as e:
                logger.error(f"Error generating embeddings: {str(e)}")
                logger.error(traceback.format_exc())
                raise

            # Prepare chunks for database
            chunk_docs = []
            es_operations = []
            
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
                chunk_id = str(ObjectId())
                
                # Create MongoDB chunk document
                chunk_doc = DocumentChunk(
                    document_id=doc_id,
                    content=chunk['content'],
                    position=chunk['position'],
                    metadata=chunk['metadata'],
                    content_stats=chunk['content_stats'],
                    quality=chunk['quality'],
                    embedding={
                        'model': config["openai"]["model"],
                        'vector': embedding,
                        'dimensions': len(embedding)
                    }
                )
                chunk_docs.append(chunk_doc.dict())

                # Prepare Elasticsearch document
                es_doc = {
                    'chunk_id': chunk_id,
                    'document_id': doc_id,
                    'content': chunk['content'],
                    'embedding': embedding,
                    'metadata': {
                        'filename': doc['filename'],
                        'mime_type': doc['mime_type'],
                        'section_type': chunk['metadata']['section_type'],
                        'section_level': chunk['metadata']['section_level']
                    }
                }
                es_operations.extend([
                    {"index": {"_index": f"{config['elasticsearch']['index']['prefix']}_chunks", "_id": chunk_id}},
                    es_doc
                ])

            # Calculate processing time
            processing_time = time.time() - start_time

            # Save chunks and update document
            try:
                logger.info(f"Saving {len(chunk_docs)} chunks to MongoDB...")
                if chunk_docs:
                    await self.db.document_chunks.insert_many(chunk_docs)
                
                logger.info("Saving embeddings to Elasticsearch...")
                if es_operations:
                    await self.es.bulk(operations=es_operations, refresh=True)
                
                # Update document with enhanced metadata
                await self.db.documents.update_one(
                    {"_id": ObjectId(doc_id)},
                    {
                        "$set": {
                            "status": "processed",
                            "file_path": processed_file,
                            "metadata": {
                                "content_type": doc["mime_type"],
                                "page_count": len(result.pages),
                                "document_structure": {
                                    "sections": section_structure
                                },
                                "language": doc_metadata["language"],
                                "keywords": doc_metadata["keywords"],
                                "processing_time": processing_time
                            },
                            "content_stats": {
                                "total_chunks": len(chunks),
                                "total_characters": len(doc_content),
                                "average_chunk_size": sum(len(c['content']) for c in chunks) / len(chunks),
                                "chunking_strategy": {
                                    "method": "smart_chunking",
                                    "parameters": {
                                        "min_size": self.chunker.min_chunk_size,
                                        "max_size": self.chunker.max_chunk_size,
                                        "overlap": self.chunker.overlap_size
                                    }
                                }
                            }
                        }
                    }
                )
                
                logger.info(f"Document processing completed in {processing_time:.2f} seconds")
                
            except Exception as e:
                logger.error(f"Error saving chunks and embeddings: {str(e)}")
                logger.error(traceback.format_exc())
                raise

        except Exception as e:
            error_msg = f"Error processing document {doc_id}: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            await self.db.documents.update_one(
                {"_id": ObjectId(doc_id)},
                {
                    "$set": {
                        "status": "failed",
                        "processing_error": error_msg
                    }
                }
            )

    async def process_pending_documents(self):
        """Process all pending documents."""
        try:
            cursor = self.db.documents.find({"status": "pending"})
            async for doc in cursor:
                logger.info(f"Processing document: {doc['_id']}")
                await self.process_document(str(doc["_id"]))
        except Exception as e:
            logger.error(f"Error in process_pending_documents: {str(e)}")
            logger.error(traceback.format_exc())

    async def run_forever(self, interval_seconds: int = 30):
        """Run the processor continuously."""
        try:
            while True:
                logger.info("Checking for pending documents...")
                await self.process_pending_documents()
                logger.info(f"Sleeping for {interval_seconds} seconds...")
                await asyncio.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            await self.close()

async def main():
    """Main entry point."""
    processor = DocumentProcessor()
    await processor.run_forever()

if __name__ == "__main__":
    asyncio.run(main()) 