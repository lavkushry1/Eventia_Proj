# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 19:57:19
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 19:58:36
"""
Authentication router module.

This module defines API endpoints for user authentication in the Eventia ticketing system.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
from datetime import timedelta

from ..core.config import settings, logger
from ..core.dependencies import get_db
from ..utils.auth import (
    Token,
    verify_password,
    get_password_hash,
    create_access_token
)

# Create router with prefix
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication failed"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and generate access token.
    
    Args:
        form_data: Username and password form data
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Check if this is the admin
        if form_data.username == settings.FIRST_ADMIN_EMAIL:
            # Verify admin password
            if not form_data.password == settings.FIRST_ADMIN_PASSWORD:
                logger.warning(f"Failed admin login attempt for {form_data.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create token for admin with admin flag
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": form_data.username, "is_admin": True},
                expires_delta=access_token_expires
            )
            
            logger.info(f"Admin login successful: {form_data.username}")
            
            return {"access_token": access_token, "token_type": "bearer"}
        
        # Regular user or custom admin login from database would be implemented here
        
        # If no matching user found
        logger.warning(f"Failed login attempt for non-existent user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication"
        )

@router.post("/verify-token", response_model=Dict[str, Any])
async def verify_token(token: str):
    """
    Verify a token is valid and not expired.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Token verification result
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # This will use the same mechanisms as the get_current_user dependency
        # The token is decoded and checked for validity
        from ..core.dependencies import get_current_user
        user = await get_current_user(token)
        
        return {
            "valid": True,
            "user": user["sub"],
            "is_admin": user.get("is_admin", False)
        }
    
    except Exception as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return {
            "valid": False,
            "error": "Invalid or expired token"
        }
