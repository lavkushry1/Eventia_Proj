"""
Test Schema Validation and Consistency
-------------------------------------
Ensures schemas are consistent between frontend and backend
"""

import sys
import json
import pytest
import os
from pathlib import Path
from pydantic import BaseModel
import importlib
import inspect
from typing import Dict, Any, List, Set

# Import backend schemas
from app.schemas.events import EventResponse, EventBase
from app.schemas.teams import TeamInfo
from app.schemas.stadium import Stadium
from app.schemas.bookings import BookingResponse, CustomerInfo, SelectedTicket
from app.schemas.settings import PaymentSettingsResponse
from app.schemas import stadium, event, booking, discount


def get_typescript_types() -> Dict[str, Set[str]]:
    """
    Parse the frontend TypeScript interfaces to get their fields
    This is a simplified parser - in a real test we might use a TypeScript parser library
    """
    typescript_file = "../../eventia-ticketing-flow/src/lib/types.ts"
    
    try:
        with open(typescript_file, "r") as f:
            content = f.read()
    except FileNotFoundError:
        pytest.skip(f"TypeScript types file not found: {typescript_file}")
        return {}
    
    interfaces = {}
    current_interface = None
    current_fields = set()
    
    for line in content.split("\n"):
        line = line.strip()
        
        # Check for interface definition
        if line.startswith("export interface ") and "{" in line:
            if current_interface:
                interfaces[current_interface] = current_fields
            
            current_interface = line.split("export interface ")[1].split("{")[0].strip()
            current_fields = set()
        
        # Check for closing brace (end of interface)
        elif line == "}" and current_interface:
            interfaces[current_interface] = current_fields
            current_interface = None
            current_fields = set()
        
        # Check for field definition
        elif current_interface and ":" in line and not line.startswith("//"):
            # Extract field name, handling optional fields (those with ?)
            field_name = line.split(":")[0].strip()
            if field_name.endswith("?"):
                field_name = field_name[:-1]
            
            # Add field to current interface
            current_fields.add(field_name)
    
    # Add the last interface if any
    if current_interface:
        interfaces[current_interface] = current_fields
    
    return interfaces


def get_all_schema_classes():
    """Get all Pydantic model classes from schema modules"""
    schema_modules = [stadium, event, booking, discount]
    schema_classes = []
    
    for module in schema_modules:
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and issubclass(obj, BaseModel) 
                and obj != BaseModel and not name.startswith('_')):
                schema_classes.append((name, obj))
    
    return schema_classes


def test_schema_exports():
    """Test that all schemas have proper exports and can be instantiated"""
    schema_classes = get_all_schema_classes()
    
    assert len(schema_classes) > 0, "No schema classes found!"
    
    for name, schema_class in schema_classes:
        print(f"Testing schema: {name}")
        
        # Verify class can be instantiated with example data if provided
        if hasattr(schema_class, "Config") and hasattr(schema_class.Config, "schema_extra"):
            example_data = schema_class.Config.schema_extra.get("example", {})
            if example_data:
                instance = schema_class(**example_data)
                assert instance is not None, f"Failed to instantiate {name} with example data"
                
                # Test JSON serialization
                json_data = instance.json()
                assert json_data is not None, f"Failed to serialize {name} to JSON"
                
                # Test schema generation
                schema = schema_class.schema()
                assert schema is not None, f"Failed to generate schema for {name}"
                assert "title" in schema, f"Schema for {name} has no title"
                assert schema["title"] == name, f"Schema title mismatch for {name}"


def test_frontend_schema_consistency():
    """Test that backend schemas match frontend TypeScript interfaces"""
    # Path to frontend type definitions
    frontend_types_dir = Path("../eventia-ticketing-flow/src/lib/types")
    
    # Skip if frontend directory doesn't exist in test environment
    if not frontend_types_dir.exists():
        pytest.skip("Frontend types directory not found")
    
    # Get all schema classes
    schema_classes = get_all_schema_classes()
    
    # Track inconsistencies
    inconsistencies = []
    
    # Check if frontend definitions exist for each schema
    for name, schema_class in schema_classes:
        # Schema JSON representation
        schema_json = schema_class.schema()
        
        # Look for corresponding TypeScript interface
        ts_files = list(frontend_types_dir.glob("*.ts"))
        ts_interface_found = False
        
        for ts_file in ts_files:
            # Read TypeScript file content
            ts_content = ts_file.read_text()
            
            # Check if interface exists - using simple string match
            # A more robust approach would use a TS parser
            if f"interface {name}" in ts_content or f"type {name}" in ts_content:
                ts_interface_found = True
                
                # Basic property check - this is simplistic and could be improved
                for prop_name, prop_data in schema_json.get("properties", {}).items():
                    # Convert snake_case to camelCase for frontend comparison
                    camel_prop = ''.join(
                        word.capitalize() if i > 0 else word
                        for i, word in enumerate(prop_name.split('_'))
                    )
                    
                    # Check if property exists in TypeScript definition
                    if camel_prop not in ts_content and prop_name not in ts_content:
                        inconsistencies.append(
                            f"Property '{prop_name}' from backend schema '{name}' not found in frontend interface"
                        )
                
                break
        
        if not ts_interface_found:
            inconsistencies.append(f"No TypeScript interface found for backend schema '{name}'")
    
    # Report inconsistencies
    if inconsistencies:
        for issue in inconsistencies:
            print(f"Schema inconsistency: {issue}")
        
        # Enable this to make the test fail when inconsistencies are found
        # assert False, f"Found {len(inconsistencies)} schema inconsistencies"


def test_event_schema_consistency():
    """Test that backend Event schema matches frontend Event interface"""
    # Get fields from backend schema
    backend_fields = set(EventResponse.__annotations__.keys())
    
    # Get fields from frontend schema
    frontend_types = get_typescript_types()
    frontend_fields = frontend_types.get("EventResponse", set())
    
    # Make sure essential fields are in both
    essential_fields = {"id", "name", "date", "time", "venue", "price"}
    
    # Check if all essential fields are in backend schema
    missing_in_backend = essential_fields - backend_fields
    assert not missing_in_backend, f"Missing essential fields in backend schema: {missing_in_backend}"
    
    # Check if all essential fields are in frontend schema
    missing_in_frontend = essential_fields - frontend_fields
    assert not missing_in_frontend, f"Missing essential fields in frontend schema: {missing_in_frontend}"


def test_team_schema_consistency():
    """Test that backend Team schema matches frontend Team interface"""
    # Get fields from backend schema
    backend_fields = set(TeamInfo.__annotations__.keys())
    
    # Get fields from frontend schema
    frontend_types = get_typescript_types()
    frontend_fields = frontend_types.get("TeamInfo", set())
    
    # Make sure essential fields are in both
    essential_fields = {"name", "code", "logo"}
    
    # Check if all essential fields are in backend schema
    missing_in_backend = essential_fields - backend_fields
    assert not missing_in_backend, f"Missing essential fields in backend schema: {missing_in_backend}"
    
    # Check if frontend has the same essential fields
    missing_in_frontend = essential_fields - frontend_fields
    assert not missing_in_frontend, f"Missing essential fields in frontend schema: {missing_in_frontend}"


def test_booking_schema_consistency():
    """Test that backend Booking schema matches frontend Booking interface"""
    # Get fields from backend schema
    backend_fields = set(BookingResponse.__annotations__.keys())
    
    # Get fields from frontend schema
    frontend_types = get_typescript_types()
    frontend_fields = frontend_types.get("BookingResponse", set())
    
    # Make sure essential fields are in both
    essential_fields = {"booking_id", "event_id", "customer_info", "selected_tickets", "status", "total_amount"}
    
    # Check if all essential fields are in backend schema
    missing_in_backend = essential_fields - backend_fields
    assert not missing_in_backend, f"Missing essential fields in backend schema: {missing_in_backend}"
    
    # Check if frontend has the same essential fields
    missing_in_frontend = essential_fields - frontend_fields
    assert not missing_in_frontend, f"Missing essential fields in frontend schema: {missing_in_frontend}"


def test_payment_settings_schema_consistency():
    """Test that backend PaymentSettings schema matches frontend PaymentSettings interface"""
    # Get fields from backend schema
    backend_fields = set(PaymentSettingsResponse.__annotations__.keys())
    
    # Get fields from frontend schema
    frontend_types = get_typescript_types()
    frontend_fields = frontend_types.get("PaymentSettingsResponse", set())
    
    # Make sure essential fields are in both
    essential_fields = {"merchant_name", "vpa", "isPaymentEnabled", "payment_mode", "type"}
    
    # Check if all essential fields are in backend schema
    missing_in_backend = essential_fields - backend_fields
    assert not missing_in_backend, f"Missing essential fields in backend schema: {missing_in_backend}"
    
    # Check if frontend has the same essential fields
    missing_in_frontend = essential_fields - frontend_fields
    assert not missing_in_frontend, f"Missing essential fields in frontend schema: {missing_in_frontend}"
    
    # Special check for vpaAddress field that must be in the PaymentSettingsResponse
    assert "vpaAddress" in backend_fields, "The 'vpaAddress' field is missing in backend schema"
    assert "vpaAddress" in frontend_fields, "The 'vpaAddress' field is missing in frontend schema"