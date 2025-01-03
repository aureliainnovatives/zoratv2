from typing import Dict, List, Optional, Literal
from pydantic import Field
from bson import ObjectId

from app.models.base import MongoBaseModel

DocumentStatus = Literal[
    "pending",           # Initial state when document is uploaded
    "parsing",          # Document is being parsed by docling
    "parsed",           # Document has been parsed successfully
    "generating_embeddings",  # Generating embeddings
    "processed",        # All processing complete
    "failed"            # Processing failed
]

class DocumentChunk(MongoBaseModel):
    """Represents a chunk of a document."""
    document_id: str = Field(..., description="Reference to parent document")
    content: str = Field(..., description="The text content of the chunk")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata about the chunk")
    embedding_id: Optional[str] = Field(None, description="Reference to vector embedding")
    page_number: Optional[int] = Field(None, description="Page number in the original document")
    chunk_number: int = Field(..., description="Sequential number of the chunk")

    class Config:
        collection_name = "document_chunks"
        json_encoders = {ObjectId: str}

class Document(MongoBaseModel):
    """Represents a document in the system."""
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Path to the stored file")
    mime_type: str = Field(..., description="MIME type of the document")
    status: DocumentStatus = Field(default="pending", description="Processing status of the document")
    processing_error: Optional[str] = Field(None, description="Error message if processing failed")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata about the document")
    chunk_ids: List[str] = Field(default_factory=list, description="References to document chunks")
    total_chunks: Optional[int] = Field(None, description="Total number of chunks")
    
    class Config:
        collection_name = "documents"
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True 