"""
JSON Utilities
-------------
Utilities for JSON serialization/deserialization
"""

import json
from datetime import datetime, date, time
from bson import ObjectId
from typing import Any, Dict, Union


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle datetime objects and MongoDB ObjectIds
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, (date, time)):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        # For Pydantic models that have a dict method
        if hasattr(obj, "dict") and callable(getattr(obj, "dict")):
            return obj.dict()
        # For Pydantic v2 models with model_dump method
        if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
            return obj.model_dump()
        return super().default(obj)


def json_serializer(obj: Any) -> Any:
    """
    JSON serializer function for objects not serializable by default json code
    
    Args:
        obj: Object to serialize
    
    Returns:
        JSON serializable object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, (date, time)):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    if hasattr(obj, "dict") and callable(getattr(obj, "dict")):
        return obj.dict()
    if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
        return obj.model_dump()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def serialize_dict(data: Dict) -> Dict:
    """
    Serialize a dictionary to ensure all values are JSON serializable.
    This handles nested dictionaries, lists, and special types like 
    datetime and ObjectId.
    
    Args:
        data: Dictionary to serialize
    
    Returns:
        Serialized dictionary
    """
    if data is None:
        return None
        
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = serialize_dict(value)
        elif isinstance(value, list):
            result[key] = [
                serialize_dict(item) if isinstance(item, dict) else 
                str(item) if isinstance(item, (datetime, date, time, ObjectId)) else item
                for item in value
            ]
        elif isinstance(value, (datetime, date, time, ObjectId)):
            result[key] = str(value)
        elif hasattr(value, "dict") and callable(getattr(value, "dict")):
            result[key] = value.dict()
        elif hasattr(value, "model_dump") and callable(getattr(value, "model_dump")):
            result[key] = value.model_dump()
        else:
            result[key] = value
    return result