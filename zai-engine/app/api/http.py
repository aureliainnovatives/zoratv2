from fastapi import APIRouter
from app.api.endpoints import documents, search

api_router = APIRouter()

# Document endpoints
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

# Search endpoints
api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
) 