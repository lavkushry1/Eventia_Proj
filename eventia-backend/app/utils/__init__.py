"""
Utils package containing helper functions and utilities for the Eventia API.
"""

from app.utils.helpers import (
    generate_unique_id,
    generate_event_id,
    generate_booking_id,
    generate_user_id,
    generate_ticket_id,
    generate_payment_id,
    generate_settings_id,
    generate_correlation_id,
    generate_qr_code,
    generate_ticket_qr,
    format_currency,
    format_phone_number,
    format_datetime,
    calculate_expiry_time,
    create_success_response,
    create_error_response,
    paginate_results,
)

from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    get_current_user_data,
    is_admin,
    is_staff_or_admin,
    generate_password_reset_token,
    verify_password_reset_token,
)

__all__ = [
    # Helpers
    "generate_unique_id",
    "generate_event_id",
    "generate_booking_id",
    "generate_user_id",
    "generate_ticket_id",
    "generate_payment_id",
    "generate_settings_id",
    "generate_correlation_id",
    "generate_qr_code",
    "generate_ticket_qr",
    "format_currency",
    "format_phone_number",
    "format_datetime",
    "calculate_expiry_time",
    "create_success_response",
    "create_error_response",
    "paginate_results",
    
    # Auth
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_token",
    "get_current_user_data",
    "is_admin",
    "is_staff_or_admin",
    "generate_password_reset_token",
    "verify_password_reset_token",
] 