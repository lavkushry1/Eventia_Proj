import logging
import random
import string
import time
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union

import qrcode
from qrcode.image.svg import SvgPathImage
from qrcode.image.pil import PilImage
import base64

# Configure logger
logger = logging.getLogger("eventia.utils")


def generate_unique_id(prefix: str = "", length: int = 8) -> str:
    """
    Generate a unique ID with optional prefix
    
    Args:
        prefix: Optional prefix for the ID
        length: Length of the random part
        
    Returns:
        A unique string ID
    """
    timestamp = int(time.time())
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    # If prefix is provided, use it, otherwise use default prefixes
    if not prefix:
        if length <= 6:
            prefix = "id_"
        else:
            prefix = ""
    
    return f"{prefix}{timestamp}_{random_part}"


def generate_event_id() -> str:
    """Generate a unique event ID"""
    return generate_unique_id("evt_", 6)


def generate_booking_id() -> str:
    """Generate a unique booking ID"""
    return generate_unique_id("bkg_", 6)


def generate_user_id() -> str:
    """Generate a unique user ID"""
    return generate_unique_id("usr_", 6)


def generate_ticket_id() -> str:
    """Generate a unique ticket ID"""
    return generate_unique_id("tkt_", 8)


def generate_payment_id() -> str:
    """Generate a unique payment ID"""
    return generate_unique_id("pay_", 8)


def generate_settings_id() -> str:
    """Generate a unique settings ID"""
    return generate_unique_id("set_", 6)


def generate_correlation_id() -> str:
    """Generate a correlation ID for request tracing"""
    return str(uuid.uuid4())


def generate_qr_code(data: str, size: int = 10, as_base64: bool = True, 
                    image_format: str = "PNG") -> Union[str, bytes]:
    """
    Generate a QR code for the provided data
    
    Args:
        data: The data to encode in the QR code
        size: The size of the QR code in box size
        as_base64: Whether to return as base64 encoded string
        image_format: Format of the image (PNG or SVG)
        
    Returns:
        A QR code as base64 string or bytes
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    if image_format.upper() == "SVG":
        img = qr.make_image(image_factory=SvgPathImage)
        buffer = BytesIO()
        img.save(buffer)
        if as_base64:
            return f"data:image/svg+xml;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
        return buffer.getvalue()
    else:
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        if as_base64:
            return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
        return buffer.getvalue()


def generate_ticket_qr(ticket_id: str, event_id: str, user_id: Optional[str] = None) -> str:
    """
    Generate a QR code for a ticket with verification data
    
    Args:
        ticket_id: The ticket ID
        event_id: The event ID
        user_id: Optional user ID
        
    Returns:
        A base64 encoded QR code
    """
    # Create verification data
    data = {
        "ticket_id": ticket_id,
        "event_id": event_id,
        "timestamp": int(time.time())
    }
    if user_id:
        data["user_id"] = user_id
    
    # Convert to string and generate QR
    qr_data = str(data)
    return generate_qr_code(qr_data)


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format a currency amount
    
    Args:
        amount: The amount to format
        currency: The currency code
        
    Returns:
        Formatted currency string
    """
    if currency == "INR":
        return f"₹{amount:,.2f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"


def format_phone_number(phone: str) -> str:
    """
    Format a phone number for display
    
    Args:
        phone: The phone number to format
        
    Returns:
        Formatted phone number
    """
    # Simple formatting for Indian numbers
    if len(phone) == 10:
        return f"+91 {phone[:5]} {phone[5:]}"
    elif len(phone) > 10 and phone.startswith("+"):
        country_code = phone[:3]
        number = phone[3:]
        return f"{country_code} {number[:5]} {number[5:]}"
    return phone


def format_datetime(dt: datetime, format_str: str = "%d %b %Y, %I:%M %p") -> str:
    """
    Format a datetime object
    
    Args:
        dt: The datetime to format
        format_str: The format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def calculate_expiry_time(minutes: int = 30) -> datetime:
    """
    Calculate an expiry time from now
    
    Args:
        minutes: Number of minutes from now
        
    Returns:
        Expiry datetime
    """
    return datetime.now() + timedelta(minutes=minutes)


def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """
    Create a standard success response
    
    Args:
        data: The response data
        message: Success message
        
    Returns:
        Formatted response dictionary
    """
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": int(time.time())
    }


def create_error_response(message: str, error_code: str = "ERROR", 
                        details: Optional[Any] = None) -> Dict[str, Any]:
    """
    Create a standard error response
    
    Args:
        message: Error message
        error_code: Error code
        details: Optional error details
        
    Returns:
        Formatted error response dictionary
    """
    response = {
        "status": "error",
        "error": {
            "code": error_code,
            "message": message,
        },
        "timestamp": int(time.time())
    }
    
    if details:
        response["error"]["details"] = details
    
    return response


def paginate_results(items: List[Any], page: int = 1, page_size: int = 20) -> Tuple[List[Any], Dict[str, int]]:
    """
    Paginate a list of items
    
    Args:
        items: List of items to paginate
        page: Current page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Tuple of (paginated_items, pagination_info)
    """
    total_items = len(items)
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    
    # Ensure page is within bounds
    page = max(1, min(page, total_pages))
    
    # Calculate start and end indices
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)
    
    # Get the items for the current page
    paginated_items = items[start_idx:end_idx]
    
    # Create pagination info
    pagination_info = {
        "total": total_items,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }
    
    return paginated_items, pagination_info 