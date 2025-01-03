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

from app.models.document import Document, DocumentChunk
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
        
        # Initialize parser
        self.parser = DocumentConverter()
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config["openai"]["api_key"],
            model=config["openai"]["model"]
        )

    async def close(self):
        """Close connections."""
        await self.es.close()
        self.mongo_client.close()

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks based on settings."""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            # Get chunk with overlap
            end = start + config["docling"]["chunking"]["size"]
            chunk = text[start:end]
            
            # If not at the end, try to break at a sentence or paragraph
            if end < text_len:
                # Try to find a good break point
                break_chars = ["\n\n", ".", "!", "?"]
                for char in break_chars:
                    last_break = chunk.rfind(char)
                    if last_break != -1:
                        end = start + last_break + 1
                        chunk = text[start:end]
                        break
            
            chunks.append(chunk)
            start = end - config["docling"]["chunking"]["overlap"]
        
        return [c for c in chunks if c.strip()]

    async def process_document(self, doc_id: str):
        """Process a single document."""
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
            
            # Parse document using docling with timeout
            try:
                logger.info(f"Starting to parse document: {doc['file_path']}")
                result = self.parser.convert(doc["file_path"])
                
                # Check if processing time exceeds limit
                if time.time() - start_time > config["docling"]["performance"]["timeout_seconds"]:
                    raise TimeoutError("Document processing exceeded timeout limit")
                
                logger.info(f"Successfully parsed document. Found {len(result.pages)} pages.")
                
            except Exception as e:
                logger.error(f"Error parsing document: {str(e)}")
                logger.error(traceback.format_exc())
                raise
            
            # Extract text content
            doc_content = ""
            for page in result.pages:
                page_text = []
                for cell in page.cells:
                    if hasattr(cell, 'text') and cell.text:
                        page_text.append(cell.text)
                doc_content += "\n".join(page_text) + "\n\n"

            logger.info(f"Extracted {len(doc_content)} characters of text content")

            # Move file to processed directory
            processed_path = get_storage_path(config["storage"]["directories"]["processed"])
            processed_file = os.path.join(processed_path, os.path.basename(doc["file_path"]))
            shutil.move(doc["file_path"], processed_file)

            # Update status to generating embeddings
            await self.db.documents.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": {"status": "generating_embeddings"}}
            )

            # Split content into chunks based on settings
            chunks_content = self.chunk_text(doc_content)
            logger.info(f"Created {len(chunks_content)} text chunks")

            try:
                logger.info("Generating embeddings...")
                embeddings_list = await self.embeddings.aembed_documents(chunks_content)
                logger.info(f"Generated {len(embeddings_list)} embeddings")
            except Exception as e:
                logger.error(f"Error generating embeddings: {str(e)}")
                logger.error(traceback.format_exc())
                raise

            # Prepare chunks and ES operations
            chunks = []
            chunk_ids = []
            es_operations = []

            for idx, (content, embedding) in enumerate(zip(chunks_content, embeddings_list)):
                chunk_id = ObjectId()
                chunk_id_str = str(chunk_id)
                chunk_ids.append(chunk_id_str)

                # Create MongoDB chunk
                chunk = {
                    "_id": chunk_id,
                    "document_id": doc_id,
                    "content": content,
                    "metadata": {
                        "section_type": "paragraph",
                        "section_number": idx + 1,
                        "page_number": idx // 5 + 1
                    },
                    "page_number": idx // 5 + 1,
                    "chunk_number": idx,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                chunks.append(chunk)

                # Prepare Elasticsearch document
                es_doc = {
                    "chunk_id": chunk_id_str,
                    "document_id": doc_id,
                    "content": content,
                    "embedding": embedding,
                    "metadata": {
                        "filename": doc["filename"],
                        "mime_type": doc["mime_type"],
                        "section_number": idx + 1,
                        "page_number": idx // 5 + 1
                    }
                }
                es_operations.append(
                    {"index": {"_index": f"{config['elasticsearch']['index']['prefix']}_chunks", "_id": chunk_id_str}}
                )
                es_operations.append(es_doc)

            # Save chunks and embeddings
            if chunks:
                try:
                    logger.info(f"Saving {len(chunks)} chunks to MongoDB...")
                    await self.db.document_chunks.insert_many(chunks)
                    
                    logger.info("Saving embeddings to Elasticsearch...")
                    await self.es.bulk(operations=es_operations, refresh=True)
                    
                    # Calculate processing time
                    processing_time = time.time() - start_time

                    logger.info(f"Document processing completed in {processing_time:.2f} seconds")

                    # Update document status
                    await self.db.documents.update_one(
                        {"_id": ObjectId(doc_id)},
                        {
                            "$set": {
                                "status": "processed",
                                "file_path": processed_file,
                                "chunk_ids": chunk_ids,
                                "total_chunks": len(chunks),
                                "metadata": {
                                    "total_chunks": len(chunks),
                                    "document_type": doc["mime_type"],
                                    "content_length": len(doc_content),
                                    "raw_content": doc_content[:1000],
                                    "total_pages": len(result.pages),
                                    "processing_time_seconds": processing_time,
                                    "docling_settings": {
                                        "chunking": config["docling"]["chunking"],
                                        "performance": config["docling"]["performance"],
                                        "processing": config["docling"]["processing"]
                                    }
                                }
                            }
                        }
                    )
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
            # Find pending documents
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