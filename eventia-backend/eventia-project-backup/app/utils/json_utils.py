"""
JSON Utilities
-------------
Utilities for JSON serialization/deserialization
"""

import json
from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, Union


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle datetime objects and MongoDB ObjectIds
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
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
    if isinstance(obj, ObjectId):
        return str(obj)
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
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = serialize_dict(value)
        elif isinstance(value, list):
            result[key] = [
                serialize_dict(item) if isinstance(item, dict) else 
                str(item) if isinstance(item, (datetime, ObjectId)) else item
                for item in value
            ]
        elif isinstance(value, (datetime, ObjectId)):
            result[key] = str(value)
        else:
            result[key] = value
    return result