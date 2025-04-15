from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.core.config import settings
from app.api.dependencies import AdminUser, CurrentUser

router = APIRouter(prefix="/config", tags=["Configuration"])


@router.get("/public")
async def get_public_config() -> Dict[str, Any]:
    """
    Get public configuration settings for the frontend
    
    Returns:
        Public configuration settings
    """
    return {
        "api_base_url": settings.API_BASE_URL,
        "payment_enabled": settings.PAYMENT_ENABLED,
        "merchant_name": settings.MERCHANT_NAME,
        "vpa_address": settings.VPA_ADDRESS,
        "default_currency": settings.DEFAULT_CURRENCY,
    }


@router.get("/admin", dependencies=[Depends(AdminUser)])
async def get_admin_config() -> Dict[str, Any]:
    """
    Get admin configuration settings for the frontend
    
    Returns:
        Admin configuration settings
    """
    return {
        "api_base_url": settings.API_BASE_URL,
        "frontend_base_url": settings.FRONTEND_BASE_URL,
        "payment_enabled": settings.PAYMENT_ENABLED,
        "merchant_name": settings.MERCHANT_NAME,
        "vpa_address": settings.VPA_ADDRESS,
        "qr_image_path": settings.QR_IMAGE_PATH,
        "payment_expiry_minutes": settings.PAYMENT_EXPIRY_MINUTES,
        "default_currency": settings.DEFAULT_CURRENCY,
        "default_payment_method": settings.DEFAULT_PAYMENT_METHOD,
        "environment": settings.ENVIRONMENT,
        "project_version": settings.PROJECT_VERSION,
    }


@router.post("/admin/update", dependencies=[Depends(AdminUser)])
async def update_admin_config(
    payment_enabled: bool = None,
    merchant_name: str = None,
    vpa_address: str = None,
    frontend_base_url: str = None,
) -> Dict[str, Any]:
    """
    Update admin configuration settings
    
    Args:
        payment_enabled: Enable or disable payments
        merchant_name: Merchant name for payments
        vpa_address: Virtual Payment Address
        frontend_base_url: Frontend base URL
        
    Returns:
        Updated configuration settings
    """
    # Note: In a real application, you would update the database here
    # and possibly refresh the settings from the database
    
    # For now, we'll just return the current settings
    # In a real implementation, you would update a settings collection in MongoDB
    return {
        "payment_enabled": payment_enabled if payment_enabled is not None else settings.PAYMENT_ENABLED,
        "merchant_name": merchant_name or settings.MERCHANT_NAME,
        "vpa_address": vpa_address or settings.VPA_ADDRESS,
        "frontend_base_url": frontend_base_url or settings.FRONTEND_BASE_URL,
    } 