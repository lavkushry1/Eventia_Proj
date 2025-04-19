#!/usr/bin/env python3
"""
Stadium import script for the Eventia application.
This script imports stadium data from the indian_stadiums.py file into the MongoDB database.
"""

import asyncio
from ..db.mongodb import engine
from ..data.indian_stadiums import INDIAN_STADIUMS
from ..models.stadium import Stadium
from datetime import datetime


async def import_stadiums() -> None:
    """Import stadiums data into the database."""
    print(f"Starting stadium import process...")

    # Count existing stadiums
    existing_count = await engine.count(Stadium)
    print(f"Found {existing_count} existing stadiums in the database")

    # Process each stadium
    imported_count = 0
    updated_count = 0

    for stadium_data in INDIAN_STADIUMS:
        # Check if stadium already exists by name
        existing_stadium = await engine.find_one(Stadium, Stadium.name == stadium_data["name"])

        # Add timestamps
        now = datetime.now()

        if existing_stadium:
            # Update existing stadium
            stadium_data["updated_at"] = now
            await engine.save(existing_stadium)
            updated_count += 1
            print(f"Updated stadium: {stadium_data['name']}")
        else:
            # Insert new stadium
            stadium_data["created_at"] = now
            stadium = Stadium(**stadium_data)
            await engine.save(stadium)
            imported_count += 1
            print(f"Imported new stadium: {stadium_data['name']}")

    # Print summary
    print(f"\nImport process completed:")
    print(f"- {imported_count} new stadiums imported")
    print(f"- {updated_count} existing stadiums updated")
    print(f"- {existing_count + imported_count} total stadiums in database")

if __name__ == "__main__":
    asyncio.run(import_stadiums())