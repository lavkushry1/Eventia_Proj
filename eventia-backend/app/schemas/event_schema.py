"""
Event Schema
----------
This module defines schemas for event-related operations.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from datetime import datetime
from app.config.constants import EventStatus, EventCategory

class TeamSchema(Schema):
    """Team schema for event teams."""
    name = fields.Str(required=True)
    code = fields.Str(required=True)
    color = fields.Str(default='#000000')
    secondary_color = fields.Str(default='#FFFFFF')

class TicketTypeSchema(Schema):
    """Ticket type schema for event ticket types."""
    id = fields.Str()
    name = fields.Str(required=True)
    price = fields.Float(required=True, validate=validate.Range(min=0))
    available = fields.Int(required=True, validate=validate.Range(min=0))
    description = fields.Str()

class EventTeamsSchema(Schema):
    """Event teams schema."""
    home = fields.Nested(TeamSchema, required=True)
    away = fields.Nested(TeamSchema, required=True)

class EventSchema(Schema):
    """Schema for event data."""
    id = fields.Str()
    name = fields.Str(required=True)
    description = fields.Str()
    date = fields.Str(required=True)
    time = fields.Str(required=True)
    venue = fields.Str(required=True)
    price = fields.Float(required=True, validate=validate.Range(min=0))
    availability = fields.Int(required=True, validate=validate.Range(min=0))
    image_url = fields.Str()
    category = fields.Str(validate=validate.OneOf(EventCategory.values()))
    is_featured = fields.Bool(default=False)
    status = fields.Str(validate=validate.OneOf(EventStatus.values()), default=EventStatus.AVAILABLE)
    teams = fields.Nested(EventTeamsSchema)
    ticketTypes = fields.List(fields.Nested(TicketTypeSchema))
    created_at = fields.DateTime(default=datetime.now)
    updated_at = fields.DateTime(default=datetime.now)
    
    @validates('date')
    def validate_date(self, value):
        """Validate date format."""
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValidationError('Invalid date format. Use YYYY-MM-DD')
    
    @validates('time')
    def validate_time(self, value):
        """Validate time format."""
        try:
            datetime.strptime(value, '%H:%M')
        except ValueError:
            raise ValidationError('Invalid time format. Use HH:MM')

class EventResponseSchema(Schema):
    """Schema for event response data."""
    id = fields.Str(required=True)
    title = fields.Str(required=True, attribute='name')
    description = fields.Str()
    date = fields.Str(required=True)
    time = fields.Str(required=True)
    venue = fields.Str(required=True)
    ticket_price = fields.Float(required=True, attribute='price')
    tickets_available = fields.Int(required=True, attribute='availability')
    image_url = fields.Str()
    category = fields.Str()
    is_featured = fields.Bool()
    status = fields.Str()
    
    # Team data
    team_home = fields.Method('get_team_home')
    team_away = fields.Method('get_team_away')
    
    # Ticket types
    ticket_types = fields.Method('get_ticket_types')
    
    def get_team_home(self, obj):
        """Get home team data."""
        if not obj.get('teams'):
            return None
        
        home = obj['teams'].get('home', {})
        return {
            "name": home.get('name', ''),
            "logo": home.get('code', '').lower(),
            "primary_color": home.get('color', '#000000'),
            "secondary_color": home.get('secondary_color', '#FFFFFF')
        }
    
    def get_team_away(self, obj):
        """Get away team data."""
        if not obj.get('teams'):
            return None
        
        away = obj['teams'].get('away', {})
        return {
            "name": away.get('name', ''),
            "logo": away.get('code', '').lower(),
            "primary_color": away.get('color', '#000000'),
            "secondary_color": away.get('secondary_color', '#FFFFFF')
        }
    
    def get_ticket_types(self, obj):
        """Get ticket types."""
        ticket_types = obj.get('ticketTypes', [])
        
        if not ticket_types:
            # Create default ticket type
            return [{
                "id": f"tkt_default_{obj.get('id', 'unknown')}",
                "name": "Standard",
                "price": obj.get('price', 0),
                "available": obj.get('availability', 0),
                "description": "Standard ticket"
            }]
        
        return ticket_types

class EventCreateSchema(EventSchema):
    """Schema for creating events."""
    
    @post_load
    def make_event(self, data, **kwargs):
        """Process data after validation."""
        # Generate unique ID if not provided
        if 'id' not in data:
            data['id'] = f"evt_{int(datetime.now().timestamp())}"
        
        # Set timestamps
        data['created_at'] = datetime.now()
        data['updated_at'] = datetime.now()
        
        return data

class EventUpdateSchema(Schema):
    """Schema for updating events."""
    name = fields.Str()
    description = fields.Str()
    date = fields.Str()
    time = fields.Str()
    venue = fields.Str()
    price = fields.Float(validate=validate.Range(min=0))
    availability = fields.Int(validate=validate.Range(min=0))
    image_url = fields.Str()
    category = fields.Str(validate=validate.OneOf(EventCategory.values()))
    is_featured = fields.Bool()
    status = fields.Str(validate=validate.OneOf(EventStatus.values()))
    teams = fields.Nested(EventTeamsSchema)
    ticketTypes = fields.List(fields.Nested(TicketTypeSchema))
    
    @validates('date')
    def validate_date(self, value):
        """Validate date format."""
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValidationError('Invalid date format. Use YYYY-MM-DD')
    
    @validates('time')
    def validate_time(self, value):
        """Validate time format."""
        try:
            datetime.strptime(value, '%H:%M')
        except ValueError:
            raise ValidationError('Invalid time format. Use HH:MM')
    
    @post_load
    def update_timestamp(self, data, **kwargs):
        """Update timestamp on validation."""
        data['updated_at'] = datetime.now()
        return data 