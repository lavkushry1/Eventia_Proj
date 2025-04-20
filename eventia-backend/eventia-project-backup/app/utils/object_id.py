"""
MongoDB ObjectId utility
-----------------------
Utility class for handling MongoDB ObjectId in Pydantic models
"""

from bson import ObjectId
from pydantic import BaseModel


class PyObjectId(ObjectId):
    """Custom type for handling MongoDB ObjectId in Pydantic models"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        """Validate the ObjectId"""
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator, _field):
        """Modify the schema to represent ObjectId as string - Updated for Pydantic v2"""
        return {"type": "string"}