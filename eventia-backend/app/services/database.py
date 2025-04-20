"""
Database service
--------------
A service class for interacting with MongoDB database
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

from ..config import settings
from ..utils.logger import logger


class Database:
    """Database service for MongoDB operations"""
    
    _client = None
    _db = None
    
    @classmethod
    async def get_client(cls) -> AsyncIOMotorClient:
        """Get MongoDB client (create if it doesn't exist)"""
        if cls._client is None:
            try:
                cls._client = AsyncIOMotorClient(settings.MONGODB_URL)
                logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}")
            except Exception as e:
                logger.error(f"Error connecting to MongoDB: {str(e)}")
                raise e
        return cls._client
    
    @classmethod
    async def get_db(cls):
        """Get database instance"""
        if cls._db is None:
            client = await cls.get_client()
            cls._db = client[settings.MONGODB_DB]
            logger.info(f"Using database: {settings.MONGODB_DB}")
        return cls._db
    
    @classmethod
    async def get_collection(cls, collection_name: str):
        """Get a collection by name"""
        db = await cls.get_db()
        return db[collection_name]
    
    @classmethod
    async def find(
        cls, 
        collection_name: str, 
        query: Dict[str, Any], 
        projection: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = 0,
        sort: List[Tuple[str, int]] = None
    ) -> List[Dict[str, Any]]:
        """Find documents in a collection"""
        collection = await cls.get_collection(collection_name)
        cursor = collection.find(query, projection)
        
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        if sort:
            sort_list = []
            for field, direction in sort:
                sort_direction = ASCENDING if direction == 1 else DESCENDING
                sort_list.append((field, sort_direction))
            cursor = cursor.sort(sort_list)
        
        return await cursor.to_list(length=None)
    
    @classmethod
    async def find_one(
        cls, 
        collection_name: str, 
        query: Dict[str, Any], 
        projection: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Find a single document in a collection"""
        collection = await cls.get_collection(collection_name)
        return await collection.find_one(query, projection)
    
    @classmethod
    async def count(cls, collection_name: str, query: Dict[str, Any]) -> int:
        """Count documents in a collection"""
        collection = await cls.get_collection(collection_name)
        return await collection.count_documents(query)
    
    @classmethod
    async def insert_one(cls, collection_name: str, document: Dict[str, Any]) -> bool:
        """Insert a document into a collection"""
        collection = await cls.get_collection(collection_name)
        result = await collection.insert_one(document)
        return result.acknowledged
    
    @classmethod
    async def insert_many(cls, collection_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Insert multiple documents into a collection"""
        collection = await cls.get_collection(collection_name)
        result = await collection.insert_many(documents)
        return result.acknowledged
    
    @classmethod
    async def update_one(
        cls, 
        collection_name: str, 
        query: Dict[str, Any], 
        update: Dict[str, Any],
        upsert: bool = False
    ) -> bool:
        """Update a document in a collection"""
        collection = await cls.get_collection(collection_name)
        result = await collection.update_one(query, update, upsert=upsert)
        return result.acknowledged
    
    @classmethod
    async def update_many(
        cls, 
        collection_name: str, 
        query: Dict[str, Any], 
        update: Dict[str, Any],
        upsert: bool = False
    ) -> bool:
        """Update multiple documents in a collection"""
        collection = await cls.get_collection(collection_name)
        result = await collection.update_many(query, update, upsert=upsert)
        return result.acknowledged
    
    @classmethod
    async def delete_one(cls, collection_name: str, query: Dict[str, Any]) -> bool:
        """Delete a document from a collection"""
        collection = await cls.get_collection(collection_name)
        result = await collection.delete_one(query)
        return result.acknowledged
    
    @classmethod
    async def delete_many(cls, collection_name: str, query: Dict[str, Any]) -> bool:
        """Delete multiple documents from a collection"""
        collection = await cls.get_collection(collection_name)
        result = await collection.delete_many(query)
        return result.acknowledged
    
    @classmethod
    async def aggregate(cls, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run an aggregation pipeline on a collection"""
        collection = await cls.get_collection(collection_name)
        cursor = collection.aggregate(pipeline)
        return await cursor.to_list(length=None)
    
    @classmethod
    async def create_index(cls, collection_name: str, keys: List[Tuple[str, int]], **kwargs) -> str:
        """Create an index on a collection"""
        collection = await cls.get_collection(collection_name)
        
        index_keys = []
        for field, direction in keys:
            sort_direction = ASCENDING if direction == 1 else DESCENDING
            index_keys.append((field, sort_direction))
            
        return await collection.create_index(index_keys, **kwargs)