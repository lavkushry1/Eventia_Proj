#!/usr/bin/env python3
"""
Stadium import script for the Eventia application.
This script imports stadium data from the indian_stadiums.py file into the MongoDB database.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir.parent))

from app.core.database import get_database
from app.data.indian_stadiums import INDIAN_STADIUMS
from datetime import datetime

async def import_stadiums():
    """Import stadiums data into the database."""
    print(f"Starting stadium import process...")
    
    # Connect to the database
    async with get_database() as db:
        # Count existing stadiums
        existing_count = await db.stadiums.count_documents({})
        print(f"Found {existing_count} existing stadiums in the database")
        
        # Process each stadium
        imported_count = 0
        updated_count = 0
        
        for stadium in INDIAN_STADIUMS:
            # Check if stadium already exists
            existing = await db.stadiums.find_one({"stadium_id": stadium["stadium_id"]})
            
            # Add timestamps
            now = datetime.now()
            stadium["updated_at"] = now
            
            if existing:
                # Update existing stadium
                result = await db.stadiums.update_one(
                    {"stadium_id": stadium["stadium_id"]},
                    {"$set": stadium}
                )
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"Updated stadium: {stadium['name']}")
                else:
                    print(f"No changes for stadium: {stadium['name']}")
            else:
                # Insert new stadium
                stadium["created_at"] = now
                await db.stadiums.insert_one(stadium)
                imported_count += 1
                print(f"Imported new stadium: {stadium['name']}")
        
        # Print summary
        print(f"\nImport process completed:")
        print(f"- {imported_count} new stadiums imported")
        print(f"- {updated_count} existing stadiums updated")
        print(f"- {existing_count + imported_count} total stadiums in database")

if __name__ == "__main__":
    print("Stadium Import Tool")
    print("-----------------")
    asyncio.run(import_stadiums())
    print("\nProcess completed successfully!") 