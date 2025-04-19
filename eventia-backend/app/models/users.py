"""
User model with MongoDB operations
----------------------------------
This module provides database operations for user management.
"""

from typing import Dict, Any, Optional, List
from bson import ObjectId
from datetime import datetime

from app.core.security import get_password_hash, verify_password
from app.db.mongodb import get_database

class UserModel:
    collection_name = "users"
    
    @classmethod
    async def get_collection(cls):
        db = await get_database()
        return db[cls.collection_name]
    
    @classmethod
    async def get_user(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID"""
        if not ObjectId.is_valid(user_id):
            return None
            
        users_collection = await cls.get_collection()
        return await users_collection.find_one({"_id": ObjectId(user_id)})
    
    @classmethod
    async def get_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email"""
        users_collection = await cls.get_collection()
        return await users_collection.find_one({"email": email.lower()})
    
    @classmethod
    async def authenticate_user(cls, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with email and password"""
        user = await cls.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user["hashed_password"]):
            return None
        return user
    
    @classmethod
    async def create_user(cls, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        users_collection = await cls.get_collection()
        
        user_in_db = {
            "email": user_data["email"].lower(),
            "hashed_password": get_password_hash(user_data["password"]),
            "full_name": user_data.get("full_name", ""),
            "is_active": True,
            "is_admin": user_data.get("is_admin", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = await users_collection.insert_one(user_in_db)
        user_in_db["_id"] = result.inserted_id
        
        # Remove hashed_password from return value
        user_in_db.pop("hashed_password", None)
        return user_in_db
    
    @classmethod
    async def update_user(cls, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a user"""
        if not ObjectId.is_valid(user_id):
            return None
            
        users_collection = await cls.get_collection()
        
        # Prepare update data
        update_data = {**user_data, "updated_at": datetime.utcnow()}
        
        # If password is being updated, hash it
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        # Update the user and return the updated document
        result = await users_collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            # Remove hashed_password from return value
            result.pop("hashed_password", None)
        
        return result
    
    @classmethod
    async def delete_user(cls, user_id: str) -> bool:
        """Delete a user"""
        if not ObjectId.is_valid(user_id):
            return False
            
        users_collection = await cls.get_collection()
        result = await users_collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    
    @classmethod
    async def list_users(
        cls, 
        skip: int = 0, 
        limit: int = 100, 
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """List users with pagination and filtering"""
        users_collection = await cls.get_collection()
        
        query = filters or {}
        cursor = users_collection.find(query).skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        
        # Remove hashed_password from all users
        for user in users:
            user.pop("hashed_password", None)
            
        return users
    
    @classmethod
    async def count_users(cls, filters: Dict[str, Any] = None) -> int:
        """Count users matching filters"""
        users_collection = await cls.get_collection()
        query = filters or {}
        return await users_collection.count_documents(query) 