"""
Base MongoDB models
-----------------
Base models for MongoDB with common functionality
"""

from typing import Any, Dict, Optional, Type
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict


class PyObjectId(str):
    """Custom type for ObjectId to work with Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(ObjectId(v))
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator, _field):
        return {"type": "string"}


class MongoBaseModel(BaseModel):
    """
    Base model for MongoDB collections with common methods
    """
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
    )
    
    @classmethod
    def get_collection_name(cls) -> str:
        """Get MongoDB collection name from model config"""
        return getattr(cls.model_config, "collection_name", cls.__name__.lower())
    
    @classmethod
    def from_mongo(cls, data: Dict) -> "MongoBaseModel":
        """
        Convert MongoDB data to model instance, handling ObjectId
        
        Args:
            data: MongoDB document
            
        Returns:
            Model instance
        """
        if not data:
            return None
            
        # If id is present in the data but not _id, use it as _id
        if data.get("id") and not data.get("_id"):
            data["_id"] = data.pop("id")
            
        # Convert ObjectId to string
        if "_id" in data and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
            
        # Return the model instance
        try:
            return cls.model_validate(data)
        except AttributeError:
            # Fallback for older pydantic versions
            return cls.parse_obj(data)
        
    def to_mongo(self) -> Dict[str, Any]:
        """
        Convert model to MongoDB document
        
        Returns:
            MongoDB document
        """
        # Convert the model to a dictionary
        try:
            data = self.model_dump(by_alias=True)
        except AttributeError:
            # Fallback for older pydantic versions
            data = self.dict(by_alias=True)
        
        # Handle special fields
        for field_name in ["id", "created_at", "updated_at"]:
            if field_name in data and not data.get(field_name):
                data.pop(field_name, None)
                
        # Convert string _id to ObjectId
        if "_id" in data and not isinstance(data["_id"], ObjectId):
            try:
                data["_id"] = ObjectId(data["_id"])
            except:
                pass
                
        return data