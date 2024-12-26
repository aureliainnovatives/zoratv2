import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_to_database(cls, mongodb_url: str, db_name: str):
        """Create database connection."""
        try:
            logger.info(f"Attempting to connect to MongoDB at {mongodb_url}")
            logger.info(f"Using database: {db_name}")
            
            # Create client
            cls.client = AsyncIOMotorClient(
                mongodb_url,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            
            # List all databases
            databases = await cls.client.list_database_names()
            logger.info(f"Available databases: {databases}")
            
            # Get database
            cls.db = cls.client[db_name]
            
            # Verify connection
            logger.info("Verifying MongoDB connection...")
            await cls.client.admin.command('ping')
            
            # List collections to verify database access
            collections = await cls.db.list_collection_names()
            logger.info(f"Available collections in {db_name}: {collections}")
            
            if 'llms' not in collections:
                logger.warning(f"'llms' collection not found in database {db_name}")
            else:
                # Count documents in llms collection
                count = await cls.db.llms.count_documents({})
                logger.info(f"Found {count} documents in llms collection")
                
                # Get a sample document
                sample = await cls.db.llms.find_one()
                if sample:
                    logger.info("Sample LLM document structure:")
                    logger.info(f"Keys: {list(sample.keys())}")
            
            logger.info("Successfully connected to MongoDB!")
            
        except ConnectionFailure as e:
            logger.error(f"Could not connect to MongoDB: {str(e)}")
            logger.exception("Connection failure details:")
            raise
        except ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB server selection timeout: {str(e)}")
            logger.error("Please check if MongoDB is running and accessible")
            raise
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            logger.exception("Detailed error:")
            raise

    @classmethod
    async def close_database_connection(cls):
        """Close database connection."""
        try:
            if cls.client:
                cls.client.close()
                logger.info("MongoDB connection closed")
                cls.client = None
                cls.db = None
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")
            logger.exception("Detailed error:")
            raise

    @classmethod
    def get_db(cls):
        """Get database instance."""
        if not cls.db:
            raise RuntimeError("Database connection not initialized")
        return cls.db 