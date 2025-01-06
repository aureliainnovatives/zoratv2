from typing import Dict, List, Optional, Literal, Union
from pydantic import Field, BaseModel
from bson import ObjectId
from datetime import datetime

from app.models.base import MongoBaseModel

DocumentStatus = Literal[
    "pending",           # Initial state when document is uploaded
    "parsing",          # Document is being parsed by docling
    "generating_embeddings",  # Generating embeddings
    "processed",        # All processing complete
    "failed"            # Processing failed
]

class DocumentSection(BaseModel):
    """Represents a section in document structure."""
    title: str = Field(..., description="Section title")
    level: int = Field(..., description="Section level in hierarchy")
    start_page: int = Field(..., description="Starting page of section")
    end_page: int = Field(..., description="Ending page of section")

class DocumentStructure(BaseModel):
    """Represents the structure of a document."""
    title: Optional[str] = Field(None, description="Document title")
    sections: List[DocumentSection] = Field(default_factory=list, description="Document sections")

class ChunkingStrategy(BaseModel):
    """Represents the chunking strategy used."""
    method: str = Field(..., description="Method used for chunking")
    parameters: Dict = Field(default_factory=dict, description="Parameters used in chunking")

class ContentStats(BaseModel):
    """Represents content statistics."""
    total_chunks: int = Field(default=0, description="Total number of chunks")
    total_characters: int = Field(default=0, description="Total character count")
    average_chunk_size: Optional[float] = Field(None, description="Average chunk size")
    chunking_strategy: Optional[ChunkingStrategy] = Field(None, description="Chunking strategy used")

class ProcessingSettings(BaseModel):
    """Represents document processing settings."""
    chunk_size: Optional[int] = Field(None, description="Size of chunks")
    chunk_overlap: Optional[int] = Field(None, description="Overlap between chunks")
    embedding_model: Optional[str] = Field(None, description="Embedding model used")
    processing_options: Dict = Field(default_factory=dict, description="Additional processing options")

class DocumentMetadata(BaseModel):
    """Represents document metadata."""
    content_type: Optional[str] = Field(None, description="Document content type")
    page_count: Optional[int] = Field(None, description="Total page count")
    document_structure: DocumentStructure = Field(default_factory=DocumentStructure, description="Document structure")
    language: Optional[str] = Field(None, description="Document language")
    author: Optional[str] = Field(None, description="Document author")
    created_date: Optional[datetime] = Field(None, description="Document creation date")
    modified_date: Optional[datetime] = Field(None, description="Document modification date")
    keywords: List[str] = Field(default_factory=list, description="Document keywords")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class Document(MongoBaseModel):
    """Represents a document in the system."""
    filename: str = Field(..., description="Original filename")
    original_name: str = Field(..., description="Original file name")
    mime_type: str = Field(..., description="MIME type of the document")
    size: int = Field(..., description="File size in bytes")
    file_path: str = Field(..., description="Path to the stored file")
    status: DocumentStatus = Field(default="pending", description="Processing status")
    processing_error: Optional[str] = Field(None, description="Error message if processing failed")
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata, description="Document metadata")
    content_stats: ContentStats = Field(default_factory=ContentStats, description="Content statistics")
    processing_settings: ProcessingSettings = Field(default_factory=ProcessingSettings, description="Processing settings")
    version: int = Field(default=1, description="Document version")
    created_by: Optional[str] = Field(None, description="User who created the document")
    updated_by: Optional[str] = Field(None, description="User who last updated the document")

    class Config:
        collection_name = "documents"
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True

class ChunkPosition(BaseModel):
    """Represents position information for a chunk."""
    page_number: Optional[int] = Field(None, description="Page number")
    chunk_number: int = Field(..., description="Chunk number")
    start_char: Optional[int] = Field(None, description="Starting character position")
    end_char: Optional[int] = Field(None, description="Ending character position")

class ChunkMetadata(BaseModel):
    """Represents chunk metadata."""
    section_type: str = Field(default="paragraph", description="Type of section")
    section_level: Optional[int] = Field(None, description="Section level in hierarchy")
    section_number: Optional[int] = Field(None, description="Section number")
    is_table_content: Optional[bool] = Field(None, description="Whether chunk contains table")
    is_figure_content: Optional[bool] = Field(None, description="Whether chunk contains figure")
    content_classification: Optional[str] = Field(None, description="Content classification")

class EmbeddingInfo(BaseModel):
    """Represents embedding information."""
    model: str = Field(..., description="Embedding model used")
    vector: List[float] = Field(..., description="Vector embedding")
    dimensions: int = Field(..., description="Number of dimensions")

class ChunkContentStats(BaseModel):
    """Represents chunk content statistics."""
    word_count: Optional[int] = Field(None, description="Word count")
    char_count: Optional[int] = Field(None, description="Character count")
    sentence_count: Optional[int] = Field(None, description="Sentence count")
    key_phrases: List[str] = Field(default_factory=list, description="Key phrases")

class QualityMetrics(BaseModel):
    """Represents quality metrics for a chunk."""
    coherence_score: Optional[float] = Field(None, description="Coherence score")
    relevance_score: Optional[float] = Field(None, description="Relevance score")
    completeness_score: Optional[float] = Field(None, description="Completeness score")

class DocumentChunk(MongoBaseModel):
    """Represents a chunk of a document."""
    document_id: str = Field(..., description="Reference to parent document")
    content: str = Field(..., description="The text content of the chunk")
    parent_chunk_id: Optional[str] = Field(None, description="Reference to parent chunk")
    child_chunks: List[str] = Field(default_factory=list, description="References to child chunks")
    position: ChunkPosition = Field(..., description="Position information")
    metadata: ChunkMetadata = Field(default_factory=ChunkMetadata, description="Chunk metadata")
    embedding: Optional[EmbeddingInfo] = Field(None, description="Embedding information")
    content_stats: ChunkContentStats = Field(default_factory=ChunkContentStats, description="Content statistics")
    quality: QualityMetrics = Field(default_factory=QualityMetrics, description="Quality metrics")
    version: int = Field(default=1, description="Chunk version")

    class Config:
        collection_name = "document_chunks"
        json_encoders = {ObjectId: str} 