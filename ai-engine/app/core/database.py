import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

logger = logging.getLogger(__name__)

class MongoDB:
    """MongoDB connection manager"""
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls, url: str = "mongodb://localhost:27017", db_name: str = "zoratv2"):
        """Connect to MongoDB"""
        try:
            logger.info(f"Attempting to connect to MongoDB at {url}")
            cls.client = AsyncIOMotorClient(url)
            cls.db = cls.client[db_name]
            
            # Test connection by listing databases
            await cls.client.list_database_names()
            
            # Log available databases and collections for debugging
            logger.info(f"Using database: {db_name}")
            databases = await cls.client.list_database_names()
            logger.info(f"Available databases: {databases}")
            
            logger.info("Verifying MongoDB connection...")
            collections = await cls.db.list_collection_names()
            logger.info(f"Available collections in {db_name}: {collections}")
            
            # Log sample document structure from llms collection
            if "llms" in collections:
                sample = await cls.db.llms.find_one()
                if sample:
                    logger.info("Sample LLM document structure:")
                    logger.info(f"Keys: {list(sample.keys())}")
                count = await cls.db.llms.count_documents({})
                logger.info(f"Found {count} documents in llms collection")
            
            logger.info("Successfully connected to MongoDB!")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            cls.client = None
            cls.db = None
            raise

    @classmethod
    def get_db(cls) -> Optional[AsyncIOMotorDatabase]:
        """Get database instance"""
        return cls.db

    @classmethod
    async def close(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None 