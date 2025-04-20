"""
Base MongoDB models
-----------------
Base models for MongoDB with common functionality
"""

from typing import Any, Dict, Optional, Type
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict


class PyObjectId(ObjectId):
    """Custom type for ObjectId to work with Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid ObjectId")
            v = ObjectId(v)
        return v
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator, _field):
        return {"type": "string"}
    
    # For Pydantic v2 compatibility - simplified version
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        # Return a simple schema that doesn't use pydantic_core functions
        return {"type": "string"}
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return str(super().__str__())


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
                
        return data