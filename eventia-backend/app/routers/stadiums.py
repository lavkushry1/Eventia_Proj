from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile, File
from typing import List, Optional
import uuid
from datetime import datetime
from pathlib import Path
import shutil
from fastapi.responses import JSONResponse

from app.schemas.stadium import Stadium, StadiumCreate, StadiumUpdate, StadiumList, StadiumSection
from app.core.database import get_database
from app.middleware.auth import get_current_user
from app.middleware.admin_auth import admin_required

router = APIRouter(
    prefix="/api/stadiums",
    tags=["stadiums"],
    responses={404: {"description": "Not found"}},
)

# Get all stadiums
@router.get("/", response_model=StadiumList)
async def get_all_stadiums(
    skip: int = Query(0, ge=0, description="Number of stadiums to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max number of stadiums to return"),
    city: Optional[str] = Query(None, description="Filter by city"),
    active_only: bool = Query(True, description="Filter only active stadiums")
):
    """Get all stadiums with optional filtering."""
    async with get_database() as db:
        query = {}
        if city:
            query["city"] = {"$regex": city, "$options": "i"}
        if active_only:
            query["is_active"] = True
        
        total = await db.stadiums.count_documents(query)
        cursor = db.stadiums.find(query).skip(skip).limit(limit)
        stadiums = await cursor.to_list(length=limit)
        
        return {
            "stadiums": stadiums,
            "total": total
        }

# Get a specific stadium by ID
@router.get("/{stadium_id}", response_model=Stadium)
async def get_stadium(
    stadium_id: str = Path(..., description="The ID of the stadium to get")
):
    """Get a specific stadium by ID."""
    async with get_database() as db:
        stadium = await db.stadiums.find_one({"stadium_id": stadium_id})
        if not stadium:
            raise HTTPException(status_code=404, detail="Stadium not found")
        return stadium

# Create a new stadium (admin only)
@router.post("/", response_model=Stadium, status_code=201)
async def create_stadium(
    stadium: StadiumCreate,
    admin = Depends(admin_required)
):
    """Create a new stadium (admin only)."""
    async with get_database() as db:
        # Check if stadium with same name already exists
        existing = await db.stadiums.find_one({"name": stadium.name})
        if existing:
            raise HTTPException(status_code=400, detail="Stadium with this name already exists")
        
        # Generate stadium_id from name (lowercase, spaces to underscores)
        stadium_id = stadium.name.lower().replace(" ", "_")
        
        # Create the stadium document
        now = datetime.now()
        stadium_dict = stadium.dict()
        stadium_dict.update({
            "stadium_id": stadium_id,
            "created_at": now,
            "updated_at": now
        })
        
        await db.stadiums.insert_one(stadium_dict)
        return stadium_dict

# Update a stadium (admin only)
@router.put("/{stadium_id}", response_model=Stadium)
async def update_stadium(
    stadium_update: StadiumUpdate,
    stadium_id: str = Path(..., description="The ID of the stadium to update"),
    admin = Depends(admin_required)
):
    """Update a stadium (admin only)."""
    async with get_database() as db:
        # Check if stadium exists
        existing = await db.stadiums.find_one({"stadium_id": stadium_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Stadium not found")
        
        # Update only provided fields
        update_data = {k: v for k, v in stadium_update.dict().items() if v is not None}
        if update_data:
            update_data["updated_at"] = datetime.now()
            
            # Update the document
            result = await db.stadiums.update_one(
                {"stadium_id": stadium_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=304, detail="Stadium not modified")
        
        # Return the updated stadium
        updated_stadium = await db.stadiums.find_one({"stadium_id": stadium_id})
        return updated_stadium

# Delete a stadium (admin only)
@router.delete("/{stadium_id}", status_code=204)
async def delete_stadium(
    stadium_id: str = Path(..., description="The ID of the stadium to delete"),
    admin = Depends(admin_required)
):
    """Delete a stadium (admin only)."""
    async with get_database() as db:
        # Check if stadium exists
        existing = await db.stadiums.find_one({"stadium_id": stadium_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Stadium not found")
        
        # Delete the stadium
        await db.stadiums.delete_one({"stadium_id": stadium_id})
        return None

# Get stadium sections with pricing
@router.get("/{stadium_id}/sections", response_model=List[StadiumSection])
async def get_stadium_sections(
    stadium_id: str = Path(..., description="The ID of the stadium"),
    event_id: Optional[str] = Query(None, description="Optional event ID to get event-specific pricing")
):
    """Get stadium sections with pricing information."""
    async with get_database() as db:
        stadium = await db.stadiums.find_one({"stadium_id": stadium_id})
        if not stadium:
            raise HTTPException(status_code=404, detail="Stadium not found")
        
        # If event_id is provided, check for event-specific pricing
        if event_id:
            event = await db.events.find_one({"_id": event_id})
            if not event:
                raise HTTPException(status_code=404, detail="Event not found")
            
            # If the event has custom pricing for this stadium, use that
            if event.get("stadium_pricing") and event["stadium_pricing"].get(stadium_id):
                return event["stadium_pricing"][stadium_id]
        
        # Otherwise return the default stadium sections
        return stadium["sections"]

# Upload stadium image (admin only)
@router.post("/{stadium_id}/image", status_code=201)
async def upload_stadium_image(
    stadium_id: str = Path(..., description="The ID of the stadium"),
    file: UploadFile = File(...),
    admin = Depends(admin_required)
):
    """Upload stadium image (admin only)."""
    # Check if stadium exists
    async with get_database() as db:
        stadium = await db.stadiums.find_one({"stadium_id": stadium_id})
        if not stadium:
            raise HTTPException(status_code=404, detail="Stadium not found")
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File format not allowed. Use: {', '.join(allowed_extensions)}"
        )
    
    # Create directory if it doesn't exist
    upload_dir = Path(__file__).parent.parent / "static" / "stadiums"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate safe filename
    new_filename = f"{stadium_id}.{file_extension}"
    file_path = upload_dir / new_filename
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update stadium in database with new image URL
    image_url = f"/static/stadiums/{new_filename}"
    async with get_database() as db:
        await db.stadiums.update_one(
            {"stadium_id": stadium_id},
            {"$set": {"image_url": image_url, "updated_at": datetime.now()}}
        )
    
    return JSONResponse(content={
        "message": "Stadium image uploaded successfully",
        "image_url": image_url
    })

# Upload AR model for stadium (admin only)
@router.post("/{stadium_id}/ar-model", status_code=201)
async def upload_stadium_ar_model(
    stadium_id: str = Path(..., description="The ID of the stadium"),
    file: UploadFile = File(...),
    admin = Depends(admin_required)
):
    """Upload AR model for stadium (admin only)."""
    # Check if stadium exists
    async with get_database() as db:
        stadium = await db.stadiums.find_one({"stadium_id": stadium_id})
        if not stadium:
            raise HTTPException(status_code=404, detail="Stadium not found")
    
    # Check file extension
    allowed_extensions = {'glb', 'gltf'}
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File format not allowed. Use: {', '.join(allowed_extensions)}"
        )
    
    # Create directory if it doesn't exist
    upload_dir = Path(__file__).parent.parent / "static" / "models"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate safe filename
    new_filename = f"{stadium_id}.{file_extension}"
    file_path = upload_dir / new_filename
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update stadium in database with new AR model URL
    ar_model_url = f"/static/models/{new_filename}"
    async with get_database() as db:
        await db.stadiums.update_one(
            {"stadium_id": stadium_id},
            {"$set": {"ar_model_url": ar_model_url, "updated_at": datetime.now()}}
        )
    
    return JSONResponse(content={
        "message": "Stadium AR model uploaded successfully",
        "ar_model_url": ar_model_url
    }) 