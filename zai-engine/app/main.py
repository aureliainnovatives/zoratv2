from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import config
from app.api.v1.api import api_router
from app.core.database import db
from app.services.document_service import DocumentService

app = FastAPI(
    title=config["general"]["project_name"],
    version=config["general"]["version"],
    openapi_url=f"{config['general']['api']['prefix']}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config["general"]["api"]["cors"]["origins"],
    allow_credentials=True,
    allow_methods=config["general"]["api"]["cors"]["methods"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=config["general"]["api"]["prefix"])

@app.on_event("startup")
async def startup_db_client():
    await db.connect()
    # Create Elasticsearch index on startup
    doc_service = DocumentService()
    await doc_service.create_es_index()

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 