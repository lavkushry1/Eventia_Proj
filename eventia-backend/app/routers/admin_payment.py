"""
Admin Payment Settings Router
----------------------------
Routes for managing payment settings in the admin panel
"""

import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.logger import logger
from app.schemas.settings import PaymentSettingsBase, PaymentSettingsUpdate, PaymentSettingsResponse
from app.middleware.auth import get_admin_user

router = APIRouter(
    prefix="/admin/payment-settings",
    tags=["Admin Payment Settings"],
    dependencies=[Depends(get_admin_user)]
)

# In-memory store until database setup
_payment_settings = PaymentSettingsResponse(
    merchant_name=settings.default_merchant_name,
    vpa=settings.default_vpa,
    vpaAddress=settings.default_vpa,
    isPaymentEnabled=settings.payment_enabled,
    payment_mode="vpa",
    qrImageUrl=None,
    type="payment_settings",
    updated_at=""
)


@router.get("", response_model=PaymentSettingsResponse)
async def get_payment_settings():
    """Get current payment settings"""
    try:
        # In a real implementation, would fetch from database
        logger.info("Fetching payment settings")
        return _payment_settings
    except Exception as e:
        logger.error(f"Error fetching payment settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching payment settings: {str(e)}"
        )


@router.put("", response_model=PaymentSettingsResponse)
async def update_payment_settings(settings_update: PaymentSettingsUpdate):
    """Update payment settings"""
    try:
        global _payment_settings
        
        # Update settings
        for field, value in settings_update.dict(exclude_unset=True).items():
            if value is not None:
                setattr(_payment_settings, field, value)
        
        # When changing payment mode to vpa, make sure vpaAddress is same as vpa
        if settings_update.payment_mode == "vpa":
            _payment_settings.vpaAddress = _payment_settings.vpa
        
        # Update timestamp
        from datetime import datetime
        _payment_settings.updated_at = datetime.now().isoformat()
        
        logger.info("Payment settings updated")
        return _payment_settings
    except Exception as e:
        logger.error(f"Error updating payment settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating payment settings: {str(e)}"
        )


@router.post("/qr-image", response_model=PaymentSettingsResponse)
async def upload_qr_image(
    qr_image: UploadFile = File(...),
    payment_mode: Optional[str] = Form("qr_image"),
    isPaymentEnabled: Optional[bool] = Form(True)
):
    """Upload QR image for payment"""
    try:
        global _payment_settings
        
        # Validate file type
        valid_mime_types = ["image/png", "image/jpeg", "image/jpg"]
        if qr_image.content_type not in valid_mime_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only PNG, JPEG, and JPG are supported."
            )
        
        # Create directory if it doesn't exist
        os.makedirs(settings.static_payments_path, exist_ok=True)
        
        # Generate a unique filename
        filename = f"payment_qr.png"
        file_path = settings.static_payments_path / filename
        
        # Save the uploaded file
        with open(file_path, "wb+") as file_object:
            file_object.write(await qr_image.read())
        
        # Update payment settings
        _payment_settings.qrImageUrl = f"/static/payments/{filename}"
        _payment_settings.payment_mode = payment_mode
        _payment_settings.isPaymentEnabled = isPaymentEnabled
        _payment_settings.updated_at = datetime.now().isoformat()
        
        logger.info(f"Payment QR image uploaded: {file_path}")
        return _payment_settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading QR image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading QR image: {str(e)}"
        )


@router.post("/toggle-payment", response_model=PaymentSettingsResponse)
async def toggle_payment_status(isEnabled: bool):
    """Toggle payment status (enabled/disabled)"""
    try:
        global _payment_settings
        
        # Update payment enabled status
        _payment_settings.isPaymentEnabled = isEnabled
        _payment_settings.updated_at = datetime.now().isoformat()
        
        logger.info(f"Payment status toggled: {isEnabled}")
        return _payment_settings
    except Exception as e:
        logger.error(f"Error toggling payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling payment status: {str(e)}"
        )