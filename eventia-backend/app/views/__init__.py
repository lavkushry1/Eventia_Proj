"""
Views Package Initialization
--------------------------
This package contains all route blueprints.
"""

from app.views.event_routes import event_bp
from app.views.booking_routes import booking_bp
from app.views.payment_routes import payment_bp
from app.views.admin_routes import admin_bp

__all__ = [
    'event_bp',
    'booking_bp',
    'payment_bp',
    'admin_bp'
] 