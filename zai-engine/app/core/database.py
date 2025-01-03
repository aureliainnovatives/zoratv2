from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import config

class Database:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database: AsyncIOMotorDatabase = None

    async def connect(self):
        """Connect to MongoDB."""
        if self.client is None:
            self.client = AsyncIOMotorClient(
                config["mongodb"]["connection"]["url"],
                maxPoolSize=config["mongodb"]["connection"]["max_connections"],
                minPoolSize=config["mongodb"]["connection"]["min_connections"],
                serverSelectionTimeoutMS=config["mongodb"]["options"]["timeout_ms"],
                retryWrites=config["mongodb"]["options"]["retry_writes"]
            )
            self.database = self.client[config["mongodb"]["connection"]["db_name"]]

    async def close(self):
        """Close MongoDB connection."""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.database = None

    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if self.database is None:
            raise ConnectionError("Database not initialized. Call connect() first.")
        return self.database

db = Database() 