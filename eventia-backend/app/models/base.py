"""
Base MongoDB models
------------------
Base classes for all MongoDB models
"""

from typing import Any, Dict, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict


class PyObjectId(ObjectId):
    """Custom ObjectId type for proper serialization"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator, _field):
        return {"type": "string"}


class MongoBaseModel(BaseModel):
    """Base class for all MongoDB models"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        validate_by_name=True,  # Replaces allow_population_by_field_name
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,  # For backward compatibility
        from_attributes=True,  # Replaces orm_mode
        extra="ignore"  # Allow extra fields without validation errors
    )
    
    @classmethod
    def get_indexes(cls) -> list:
        """Return list of indexes to create for this collection"""
        return []
    
    @classmethod
    def get_collection_name(cls) -> str:
        """Get the collection name for this model"""
        return getattr(cls.model_config, "collection_name", cls.__name__.lower())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dict with correct field names"""
        data = self.model_dump(by_alias=True)
        # Convert ObjectId to string
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
        return data
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]):
        """Convert MongoDB result dict to model"""
        if not data:
            return None
        
        # MongoDB returns _id as ObjectId, make sure it's converted properly
        id_field = data.pop("_id", None)
        if id_field:
            data["id"] = id_field
        
        return cls(**data)