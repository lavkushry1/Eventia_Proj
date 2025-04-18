from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import os

from ..middleware.admin_auth import admin_required
from ..models.user import User
from ..core.database import get_database

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

# Define allowed image extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload/event-poster")
async def upload_event_poster(
    event_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(admin_required)
):
    """Upload event poster image (admin only)"""
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File format not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create directory if it doesn't exist
    upload_dir = Path(__file__).parent.parent / "static" / "events"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate safe filename using event_id
    file_extension = file.filename.split('.')[-1]
    new_filename = f"{event_id}.{file_extension}"
    file_path = upload_dir / new_filename
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update event in database with new image URL
    db = await get_database()
    await db.events.update_one(
        {"id": event_id},
        {"$set": {"image_url": f"/static/events/{new_filename}"}}
    )
    
    return JSONResponse(content={
        "message": "Event poster uploaded successfully",
        "image_url": f"/static/events/{new_filename}"
    })

@router.post("/upload/venue-image")
async def upload_venue_image(
    venue_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(admin_required)
):
    """Upload venue image (admin only)"""
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File format not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create directory if it doesn't exist
    upload_dir = Path(__file__).parent.parent / "static" / "venues"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate safe filename using venue_id
    file_extension = file.filename.split('.')[-1]
    new_filename = f"{venue_id}.{file_extension}"
    file_path = upload_dir / new_filename
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update venue in database with new image URL
    db = await get_database()
    await db.venues.update_one(
        {"id": venue_id},
        {"$set": {"image_url": f"/static/venues/{new_filename}"}}
    )
    
    return JSONResponse(content={
        "message": "Venue image uploaded successfully",
        "image_url": f"/static/venues/{new_filename}"
    })

@router.post("/upload/team-logo")
async def upload_team_logo(
    team_code: str,
    file: UploadFile = File(...),
    current_user: User = Depends(admin_required)
):
    """Upload team logo (admin only)"""
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File format not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create directory if it doesn't exist
    backend_dir = Path(__file__).parent.parent
    upload_dir = backend_dir / "static" / "teams"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Use team_code as filename
    file_extension = file.filename.split('.')[-1]
    new_filename = f"{team_code.lower()}.{file_extension}"
    file_path = upload_dir / new_filename
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Copy to frontend assets directory for immediate availability
    try:
        frontend_dir = Path(__file__).parent.parent.parent.parent.parent / "eventia-ticketing-flow" / "public" / "assets" / "teams"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        frontend_path = frontend_dir / new_filename
        shutil.copy(file_path, frontend_path)
    except Exception as e:
        # Log error but continue - frontend copy is not critical
        print(f"Warning: Could not copy to frontend directory: {str(e)}")
    
    return JSONResponse(content={
        "message": "Team logo uploaded successfully",
        "image_url": f"/static/teams/{new_filename}"
    }) 