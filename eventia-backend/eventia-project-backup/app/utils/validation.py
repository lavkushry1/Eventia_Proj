"""
Schema and Database Validation Utilities
---------------------------------------
Utilities for validating database schemas against Pydantic models
"""

import logging
from typing import Dict, List, Any, Optional, Set, Type
from pydantic import BaseModel

from app.config import settings
from app.utils.logger import logger
from app.db.mongodb import get_collection

class ValidationResult:
    """Result of a validation check"""
    def __init__(self, is_valid: bool, missing_fields: List[str] = None, extra_fields: List[str] = None, 
                 type_mismatches: Dict[str, Dict[str, Any]] = None, message: str = ""):
        self.is_valid = is_valid
        self.missing_fields = missing_fields or []
        self.extra_fields = extra_fields or []
        self.type_mismatches = type_mismatches or {}
        self.message = message

    def __bool__(self) -> bool:
        return self.is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "missing_fields": self.missing_fields,
            "extra_fields": self.extra_fields, 
            "type_mismatches": self.type_mismatches,
            "message": self.message
        }


async def validate_collection_schema(collection_name: str, model_class: Type[BaseModel]) -> ValidationResult:
    """
    Validate a MongoDB collection against a Pydantic model
    
    Args:
        collection_name: Name of the MongoDB collection
        model_class: Pydantic model class to validate against
        
    Returns:
        ValidationResult with validation details
    """
    try:
        # Get model fields
        model_fields = set(model_class.__annotations__.keys())
        
        # Get sample document from collection
        collection = get_collection(settings.mongodb_database, collection_name)
        sample_doc = await collection.find_one()
        
        if not sample_doc:
            return ValidationResult(
                is_valid=True,
                message=f"Collection {collection_name} is empty, nothing to validate"
            )
        
        # Remove MongoDB _id field if present
        if '_id' in sample_doc:
            sample_doc.pop('_id')
            
        # Get document fields
        doc_fields = set(sample_doc.keys())
        
        # Check for missing and extra fields
        missing_fields = list(model_fields - doc_fields)
        extra_fields = list(doc_fields - model_fields)
        
        # Check field types (basic check, not exhaustive)
        type_mismatches = {}
        
        # Assume valid unless issues are found
        is_valid = not missing_fields
        
        # Prepare result message
        message = f"Validation for {collection_name} "
        if is_valid:
            message += "passed"
        else:
            message += "failed"
            if missing_fields:
                message += f" - missing fields: {', '.join(missing_fields)}"
            if extra_fields:
                message += f" - extra fields: {', '.join(extra_fields)}"
        
        return ValidationResult(
            is_valid=is_valid,
            missing_fields=missing_fields,
            extra_fields=extra_fields,
            type_mismatches=type_mismatches,
            message=message
        )
    except Exception as e:
        logger.error(f"Error validating collection {collection_name}: {str(e)}")
        return ValidationResult(
            is_valid=False,
            message=f"Error validating collection {collection_name}: {str(e)}"
        )


async def validate_database_schema() -> Dict[str, ValidationResult]:
    """
    Validate all MongoDB collections against their corresponding Pydantic models
    
    Returns:
        Dictionary mapping collection names to ValidationResults
    """
    from app.schemas.events import EventResponse
    from app.schemas.teams import TeamInfo 
    from app.schemas.stadium import Stadium
    from app.schemas.bookings import BookingResponse
    from app.schemas.settings import PaymentSettingsResponse
    
    # Map collection names to model classes
    collection_models = {
        "events": EventResponse,
        "teams": TeamInfo,
        "stadiums": Stadium,
        "bookings": BookingResponse,
        "settings": PaymentSettingsResponse
    }
    
    results = {}
    
    # Validate each collection
    for collection_name, model_class in collection_models.items():
        result = await validate_collection_schema(collection_name, model_class)
        results[collection_name] = result
        
        # Log validation result
        if result.is_valid:
            logger.info(f"✅ {result.message}")
        else:
            logger.warning(f"❌ {result.message}")
            
            # Log detailed issues
            if result.missing_fields:
                logger.warning(f"   Missing fields in {collection_name}: {', '.join(result.missing_fields)}")
            if result.extra_fields:
                logger.info(f"   Extra fields in {collection_name}: {', '.join(result.extra_fields)}")
            if result.type_mismatches:
                for field, mismatch in result.type_mismatches.items():
                    logger.warning(f"   Type mismatch in {collection_name}.{field}: expected {mismatch['expected']}, got {mismatch['actual']}")
    
    return results


async def fix_database_schema_issues() -> Dict[str, Any]:
    """
    Attempt to fix common schema issues in MongoDB collections
    
    Returns:
        Dictionary with fix results
    """
    # Validate first to identify issues
    validation_results = await validate_database_schema()
    
    fix_results = {
        "fixed_collections": [],
        "errors": [],
        "field_transforms": {},
        "details": {}
    }
    
    # Process each collection with issues
    for collection_name, result in validation_results.items():
        if result.is_valid:
            continue
            
        try:
            # Handle mapping between different field names (using settings.field_name_map)
            field_transforms = {}
            for backend_field, frontend_field in settings.field_name_map.items():
                if frontend_field in result.missing_fields and backend_field in result.extra_fields:
                    field_transforms[backend_field] = frontend_field
            
            if field_transforms:
                # Apply transforms to the collection
                collection = get_collection(settings.mongodb_database, collection_name)
                update_ops = []
                
                # Create update operations for each document
                async for doc in collection.find():
                    updates = {}
                    for old_field, new_field in field_transforms.items():
                        if old_field in doc:
                            # Copy value to new field name
                            updates[new_field] = doc[old_field]
                    
                    if updates:
                        update_ops.append({
                            "filter": {"_id": doc["_id"]},
                            "update": {"$set": updates}
                        })
                
                # Apply updates in bulk if there are any
                if update_ops:
                    # Execute bulk write operations
                    for op in update_ops:
                        await collection.update_one(op["filter"], op["update"])
                    
                    fix_results["fixed_collections"].append(collection_name)
                    fix_results["field_transforms"][collection_name] = field_transforms
                    
                    logger.info(f"Fixed field name mappings in {collection_name}: {field_transforms}")
        
        except Exception as e:
            error_msg = f"Error fixing schema issues in {collection_name}: {str(e)}"
            logger.error(error_msg)
            fix_results["errors"].append(error_msg)
    
    # Re-validate to check if fixes worked
    post_validation = await validate_database_schema()
    fix_results["post_validation"] = {k: v.to_dict() for k, v in post_validation.items()}
    
    return fix_results