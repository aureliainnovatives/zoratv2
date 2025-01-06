from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config
from app.api.v1.api import api_router
from app.core.database import db
from app.services.document_service import DocumentService
from app.core.initialize import initialize_nlp
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=config["general"]["project_name"],
    version=config["general"]["version"],
    debug=config["general"]["debug"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config["general"]["api"]["cors"]["origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize application components."""
    logger.info("Initializing application components...")
    
    # Initialize database
    await db.connect()
    
    # Initialize document service
    app.state.document_service = DocumentService()
    
    # Initialize NLP components
    if not initialize_nlp():
        logger.warning("NLP initialization failed - some features may not work correctly")
    
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    await db.disconnect()
    await app.state.document_service.close()

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 