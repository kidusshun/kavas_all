from pymongo import MongoClient
from app.config import settings

# Initialize MongoDB client
client = MongoClient(settings.mongodb_url, tz_aware=True)
db = client[settings.mongodb_db_name]

def get_db() -> MongoClient:
    """Dependency to get the MongoDB database instance."""
    return db