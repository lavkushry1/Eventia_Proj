from fastapi import HTTPException, Depends, Header
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Admin token from environment variable
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "supersecuretoken123")

async def verify_admin_token(authorization: str = Header(None)):
    """
    Verify the admin token from the Authorization header
    
    Returns:
        bool: True if token is valid
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail="Authorization header is missing"
        )
        
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Invalid authorization format. Use 'Bearer TOKEN'"
        )
    
    token = authorization.split(" ")[1]
    if token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=401, 
            detail="Invalid admin token"
        )
        
    return True 