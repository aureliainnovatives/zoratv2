import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routes import agent
from .core.database import MongoDB
from .repositories.llm_repository import LLMRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zorat AI Engine",
    description="AI Engine for Zorat platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection and load LLMs on startup"""
    try:
        logger.info("Connecting to MongoDB...")
        await MongoDB.connect()
        logger.info("Successfully connected to MongoDB")
        
        # Load active LLMs into cache
        logger.info("Loading active LLMs into cache...")
        llm_repository = LLMRepository()
        # TODO: Implement LLM caching if needed
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.error("Detailed error:", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown"""
    try:
        logger.info("Closing MongoDB connection...")
        await MongoDB.close()
        logger.info("Successfully closed MongoDB connection")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Zorat AI Engine"} 