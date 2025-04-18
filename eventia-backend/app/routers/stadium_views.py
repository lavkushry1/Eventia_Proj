from fastapi import APIRouter, Depends, HTTPException, Path, UploadFile, File, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import uuid
from datetime import datetime
from pathlib import Path as FilePath
import shutil
import os

from app.schemas.stadium import SeatViewImage, SeatViewImageCreate, SeatViewImageList
from app.core.database import get_database
from app.middleware.auth import get_current_user
from app.middleware.admin_auth import admin_required

# Create router
router = APIRouter(
    prefix="/api/stadiums",
    tags=["stadium views"],
    responses={404: {"description": "Not found"}},
)

# Get all seat views for a stadium
@router.get("/{stadium_id}/views", response_model=SeatViewImageList)
async def get_stadium_views(
    stadium_id: str = Path(..., description="The ID of the stadium"),
    section_id: Optional[str] = Query(None, description="Filter by section ID")
):
    """Get all seat view images for a stadium."""
    async with get_database() as db:
        # Check if stadium exists
        stadium = await db.stadiums.find_one({"stadium_id": stadium_id})
        if not stadium:
            raise HTTPException(status_code=404, detail="Stadium not found")
        
        # Build query
        query = {"stadium_id": stadium_id}
        if section_id:
            query["section_id"] = section_id
        
        # Get seat views
        cursor = db.stadium_views.find(query)
        views = await cursor.to_list(length=100)
        
        # Get total count
        total = await db.stadium_views.count_documents(query)
        
        return {
            "views": views,
            "total": total
        }

# Get a specific seat view by ID
@router.get("/{stadium_id}/views/{view_id}", response_model=SeatViewImage)
async def get_stadium_view(
    stadium_id: str = Path(..., description="The ID of the stadium"),
    view_id: str = Path(..., description="The ID of the view")
):
    """Get a specific seat view by ID."""
    async with get_database() as db:
        view = await db.stadium_views.find_one({
            "stadium_id": stadium_id,
            "view_id": view_id
        })
        
        if not view:
            raise HTTPException(status_code=404, detail="Seat view not found")
        
        return view

# Upload a new seat view image (admin only)
@router.post("/{stadium_id}/views", status_code=201, response_model=SeatViewImage)
async def upload_seat_view(
    stadium_id: str = Path(..., description="The ID of the stadium"),
    section_id: str = Query(..., description="The section ID this view represents"),
    description: str = Query(..., description="Description of the view"),
    file: UploadFile = File(...),
    admin = Depends(admin_required)
):
    """Upload a new seat view image (admin only)."""
    async with get_database() as db:
        # Check if stadium exists
        stadium = await db.stadiums.find_one({"stadium_id": stadium_id})
        if not stadium:
            raise HTTPException(status_code=404, detail="Stadium not found")
        
        # Check if section exists in the stadium
        section_exists = False
        for section in stadium.get("sections", []):
            if section.get("section_id") == section_id:
                section_exists = True
                break
        
        if not section_exists:
            raise HTTPException(
                status_code=400, 
                detail=f"Section ID {section_id} does not exist in this stadium"
            )
        
        # Check file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File format not allowed. Use: {', '.join(allowed_extensions)}"
            )
        
        # Create directory if it doesn't exist
        upload_dir = FilePath(__file__).parent.parent / "static" / "stadium_views"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate a unique ID and filename
        view_id = f"{section_id}_{uuid.uuid4().hex[:8]}"
        new_filename = f"{stadium_id}_{view_id}.{file_extension}"
        file_path = upload_dir / new_filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create the view document
        image_url = f"/static/stadium_views/{new_filename}"
        now = datetime.now()
        view_data = {
            "view_id": view_id,
            "stadium_id": stadium_id,
            "section_id": section_id,
            "image_url": image_url,
            "description": description,
            "created_at": now,
            "updated_at": now
        }
        
        # Insert into database
        await db.stadium_views.insert_one(view_data)
        
        return view_data

# Delete a seat view (admin only)
@router.delete("/{stadium_id}/views/{view_id}", status_code=204)
async def delete_seat_view(
    stadium_id: str = Path(..., description="The ID of the stadium"),
    view_id: str = Path(..., description="The ID of the view to delete"),
    admin = Depends(admin_required)
):
    """Delete a seat view (admin only)."""
    async with get_database() as db:
        # Find the view
        view = await db.stadium_views.find_one({
            "stadium_id": stadium_id,
            "view_id": view_id
        })
        
        if not view:
            raise HTTPException(status_code=404, detail="Seat view not found")
        
        # Delete from database
        await db.stadium_views.delete_one({
            "stadium_id": stadium_id,
            "view_id": view_id
        })
        
        # Try to delete the file
        if view.get("image_url"):
            file_path = (
                FilePath(__file__).parent.parent / 
                view["image_url"].lstrip("/")
            )
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Error deleting file {file_path}: {e}")
        
        return None