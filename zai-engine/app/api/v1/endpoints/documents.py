from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.services.document_service import DocumentService
from app.models.document import Document, DocumentChunk

router = APIRouter()
document_service = DocumentService()

@router.post("/upload", response_model=Document)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for processing.
    The document will be:
    1. Saved to storage
    2. Created in MongoDB with 'pending' status
    3. Will be processed by background processor
    """
    # Save file and create initial document
    document = await document_service.create_document(file)
    return document

@router.get("/search")
async def semantic_search(
    query: str = Query(..., description="Search query text"),
    limit: int = Query(5, description="Maximum number of results to return")
):
    """
    Perform semantic search across all documents.
    Returns the most semantically similar chunks to the query.
    """
    return await document_service.semantic_search(query, limit)

@router.get("/", response_model=List[Document])
async def list_documents():
    """List all documents."""
    return await document_service.list_documents()

@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: str):
    """Get a specific document by ID."""
    document = await document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/{document_id}/chunks", response_model=List[DocumentChunk])
async def get_document_chunks(document_id: str):
    """Get all chunks for a specific document."""
    chunks = await document_service.get_document_chunks(document_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found for document")
    return chunks 