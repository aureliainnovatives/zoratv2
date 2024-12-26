import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import MongoDB
from .core.config import settings
from .routes import agent, index
from .repositories.llm_repository import LLMRepository
from .utils.llm_cache import LLMCache

# Configure logging
logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(index.router, prefix=settings.API_V1_STR)
app.include_router(agent.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection and load LLMs into cache"""
    try:
        logger.info("Connecting to MongoDB...")
        await MongoDB.connect_to_database(settings.MONGODB_URL, settings.MONGODB_DB_NAME)
        logger.info("Successfully connected to MongoDB")
        
        # Load active LLMs into cache
        logger.info("Loading active LLMs into cache...")
        active_llms = await LLMRepository.get_active_llms()
        for llm in active_llms:
            LLMCache.set_llm(llm)
        logger.info(f"Loaded {len(active_llms)} active LLMs into cache")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.exception("Detailed error:")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection"""
    try:
        logger.info("Closing MongoDB connection...")
        await MongoDB.close_database_connection()
        logger.info("Successfully closed MongoDB connection")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        logger.exception("Detailed error:")
        raise 