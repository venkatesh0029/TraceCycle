from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import logging

logger = logging.getLogger(__name__)

class Database:
    client: MongoClient = None
    db = None

    def connect(self):
        try:
            mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
            self.client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping') # Check if connected
            self.db = self.client.tracecycle_db
            logger.info("Connected to MongoDB")
        except ConnectionFailure:
            logger.error("Failed to connect to MongoDB")
            self.client = None
            self.db = None

    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

db = Database()
