import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.events import EventInDB, TeamInfo, TicketType, EventStatus
from app.schemas.event_schema import EventSchema, TeamSchema, EventTeamsSchema, TicketTypeSchema
from app.schemas.booking_schema import BookingSchema, CustomerInfo, SelectedTicket
from app.schemas.users import UserInDB
from app.schemas.admin_schema import AdminInDB
from app.schemas.settings import PaymentSettingsBase, PaymentSettingsUpdate



def test_team_info_schema_valid():
    team_data = {
        "name": "Home Team",
        "code": "HT",
        "color": "#FF0000",
        "secondary_color": "#FFFFFF",
        "logo": "https://example.com/ht.png",
        "home_ground": "Stadium 1"
    }
    team = TeamInfo(**team_data)
    assert team.name == "Home Team"
    assert team.code == "HT"
    assert team.color == "#FF0000"
    assert team.secondary_color == "#FFFFFF"
    assert team.logo == "https://example.com/ht.png"
    assert team.home_ground == "Stadium 1"

def test_ticket_type_valid():
    ticket_data = {
        "id": "ticket-1",
        "name": "VIP",
        "price": 500.00,
        "available": 100,
        "description": "VIP access",
    }
    ticket = TicketType(**ticket_data)
    assert ticket.id == "ticket-1"
    assert ticket.name == "VIP"
    assert ticket.price == 500.00
    assert ticket.available == 100
    assert ticket.description == "VIP access"
    
def test_team_schema_valid():
    team_data = {
        "name": "Home Team",
        "code": "HT",
        "color": "#FF0000",
        "secondary_color": "#FFFFFF",
        "logo": "https://example.com/ht.png",
    }
    
    team = TeamSchema(**team_data)
    assert team.name == "Home Team"
    assert team.code == "HT"
    assert team.color == "#FF0000"
    assert team.secondary_color == "#FFFFFF"
    assert team.logo == "https://example.com/ht.png"


def test_team_schema_invalid_color():
    with pytest.raises(ValidationError):
        TeamSchema(
            name="Home Team", code="HT", color="invalid", secondary_color="#FFFFFF", logo=""
        )


def test_event_teams_schema_valid():
    home_team_data = {
        "name": "Home Team",
        "code": "HT",
        "color": "#FF0000",
        "secondary_color": "#FFFFFF",
        "logo": "https://example.com/ht.png",
    }
    away_team_data = {
        "name": "Away Team",
        "code": "AT",
        "color": "#0000FF",
        "secondary_color": "#FFFFFF",
        "logo": "https://example.com/at.png",
    }
    event_teams_data = {"home": home_team_data, "away": away_team_data}
    event_teams = EventTeamsSchema(**event_teams_data)
    assert event_teams.home.name == "Home Team"
    assert event_teams.away.code == "AT"


def test_ticket_type_schema_valid():
    ticket_type_data = {
        "name": "VIP",
        "price": 500.00,
        "available": 100,
        "description": "VIP access",
    }
    ticket_type = TicketTypeSchema(**ticket_type_data)
    assert ticket_type.name == "VIP"
    assert ticket_type.price == 500.00
    assert ticket_type.available == 100
    assert ticket_type.description == "VIP access"


def test_ticket_type_schema_invalid_price():
    with pytest.raises(ValidationError):
        TicketTypeSchema(name="VIP", price=-500.00, available=100)


def test_event_schema_valid():
    event_data = {
        "name": "Example Event",
        "description": "This is an example event.",
        "date": "2024-12-31",
        "time": "20:00",
        "venue": "Example Stadium",
        "price": 100.00,
        "availability": 1000,
        "category": "sports",
        "teams": {
            "home": {
                "name": "Home Team",
                "code": "HT",
                "color": "#FF0000",
                "secondary_color": "#FFFFFF",
                "logo": "https://example.com/ht.png",
            },
            "away": {
                "name": "Away Team",
                "code": "AT",
                "color": "#0000FF",
                "secondary_color": "#FFFFFF",
                "logo": "https://example.com/at.png",
            },
        },
        "ticketTypes": [
            {
                "id": "tkt-1",
                "name": "VIP",
                "price": 500.00,
                "available": 100,
                "description": "VIP access",
            },
            {
                "id": "tkt-2",
                "name": "General",
                "price": 100.00,
                "available": 900,
                "description": "General admission",
            },
        ],
    }
    event = EventSchema(**event_data)
    assert event.name == "Example Event"
    assert event.date == "2024-12-31"
    assert event.time == "20:00"
    assert event.teams.home.name == "Home Team"

def test_event_schema_invalid_price():
    with pytest.raises(ValidationError):
        EventSchema(
            name="Example Event",
            date="2024-12-31",
            time="20:00",
            venue="Example Stadium",
            price=-100.00,
            availability=1000,
            category="sports",
            teams={
                "home": {
                    "name": "Home Team",
                    "code": "HT",
                    "color": "#FF0000",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/ht.png",
                },
                "away": {
                    "name": "Away Team",
                    "code": "AT",
                    "color": "#0000FF",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/at.png",
                },
            },
            ticketTypes=[],
        )


def test_event_schema_invalid_availability():
    with pytest.raises(ValidationError):
        EventSchema(
            name="Example Event",
            date="2024-12-31",
            time="20:00",
            venue="Example Stadium",
            price=100.00,
            availability=-1000,
            category="sports",
            teams={
                "home": {
                    "name": "Home Team",
                    "code": "HT",
                    "color": "#FF0000",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/ht.png",
                },
                "away": {
                    "name": "Away Team",
                    "code": "AT",
                    "color": "#0000FF",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/at.png",
                },
            },
            ticketTypes=[],
        )


def test_event_schema_missing_name():
    with pytest.raises(ValidationError):
        EventSchema(
            date="2024-12-31",
            time="20:00",
            venue="Example Stadium",
            price=100.00,
            availability=1000,
            category="sports",
            teams={
                "home": {
                    "name": "Home Team",
                    "code": "HT",
                    "color": "#FF0000",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/ht.png",
                },
                "away": {
                    "name": "Away Team",
                    "code": "AT",
                    "color": "#0000FF",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/at.png",
                },
            },
            ticketTypes=[],
        )

def test_event_schema_invalid_status():
    with pytest.raises(ValidationError):
        EventSchema(
            name="Example Event",
            date="2024-12-31",
            time="20:00",
            venue="Example Stadium",
            price=100.00,
            availability=1000,
            category="sports",
            status="invalid",
            teams={
                "home": {
                    "name": "Home Team",
                    "code": "HT",
                    "color": "#FF0000",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/ht.png",
                },
                "away": {
                    "name": "Away Team",
                    "code": "AT",
                    "color": "#0000FF",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/at.png",
                },
            },
            ticketTypes=[],
        )

def test_event_schema_invalid_date():
    with pytest.raises(ValidationError):
        EventSchema(
            name="Example Event",
            date="invalid-date",
            time="20:00",
            venue="Example Stadium",
            price=100.00,
            availability=1000,
            category="sports",
            teams={
                "home": {
                    "name": "Home Team",
                    "code": "HT",
                    "color": "#FF0000",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/ht.png",
                },
                "away": {
                    "name": "Away Team",
                    "code": "AT",
                    "color": "#0000FF",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/at.png",
                },
            },
            ticketTypes=[],
        )


def test_event_schema_invalid_time():
    with pytest.raises(ValidationError):
        EventSchema(
            name="Example Event",
            date="2024-12-31",
            time="invalid-time",
            venue="Example Stadium",
            price=100.00,
            availability=1000,
            category="sports",
            teams={
                "home": {
                    "name": "Home Team",
                    "code": "HT",
                    "color": "#FF0000",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/ht.png",
                },
                "away": {
                    "name": "Away Team",
                    "code": "AT",
                    "color": "#0000FF",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/at.png",
                },
            },
            ticketTypes=[],
        )


def test_event_schema_missing_teams():
    with pytest.raises(ValidationError):
        EventSchema(
            name="Example Event",
            date="2024-12-31",
            time="20:00",
            venue="Example Stadium",
            price=100.00,
            availability=1000,
            category="sports",
            ticketTypes=[
                {
                    "id": "tkt-1",
                    "name": "VIP",
                    "price": 500.00,
                    "available": 100,
                    "description": "VIP access",
                },
                {
                    "id": "tkt-2",
                    "name": "General",
                    "price": 100.00,
                    "available": 900,
                    "description": "General admission",
                },
            ],
        )

def test_event_schema_missing_ticketTypes():
    with pytest.raises(ValidationError):
        EventSchema(
            name="Example Event",
            date="2024-12-31",
            time="20:00",
            venue="Example Stadium",
            price=100.00,
            availability=1000,
            category="sports",
            teams={
                "home": {
                    "name": "Home Team",
                    "code": "HT",
                    "color": "#FF0000",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/ht.png",
                },
                "away": {
                    "name": "Away Team",
                    "code": "AT",
                    "color": "#0000FF",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/at.png",
                },
            },
        )

def test_event_schema_invalid_category():
    with pytest.raises(ValidationError):
        EventSchema(name="Example Event", date="2024-12-31", time="20:00", venue="Example Stadium", price=100.00, availability=1000, category="invalid", teams={"home": {"name": "Home Team", "code": "HT", "color": "#FF0000", "secondary_color": "#FFFFFF", "logo": "https://example.com/ht.png"}, "away": {"name": "Away Team", "code": "AT", "color": "#0000FF", "secondary_color": "#FFFFFF", "logo": "https://example.com/at.png"}}, ticketTypes=[])

def test_event_in_db_valid():
    event_data = {
        "id": "evt-1",
        "title": "Example Event",
        "description": "This is an example event.",
        "date": "2024-12-31",
        "time": "20:00",
        "venue": "Example Stadium",
        "category": "sports",
        "image_url": "http://example.com/image.jpg",
        "is_featured": True,
        "status": "upcoming",
        "ticket_types": [{"id": "ticket-1", "name": "VIP", "price": 500.00, "available": 100, "description": "VIP access"}],
        "team_home": {"name": "Home Team", "code": "HT", "color": "#FF0000", "secondary_color": "#FFFFFF", "logo": "https://example.com/ht.png"},
        "team_away": {"name": "Away Team", "code": "AT", "color": "#0000FF", "secondary_color": "#FFFFFF", "logo": "https://example.com/at.png"},
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    event = EventInDB(**event_data)
    assert event.id == "evt-1"
    assert event.title == "Example Event"
    assert event.date == "2024-12-31"
    assert event.time == "20:00"
    assert event.venue == "Example Stadium"
    assert event.category == "sports"
    assert event.image_url == "http://example.com/image.jpg"
    assert event.is_featured == True
    assert event.status == "upcoming"
    assert len(event.ticket_types) == 1
    assert event.team_home.name == "Home Team"
    assert event.team_away.code == "AT"


def test_event_in_db_invalid_date():
    with pytest.raises(ValidationError):
        EventInDB(
            id="evt-1",
            title="Example Event",
            date="invalid-date",
            time="20:00",
            venue="Example Stadium",
            category="sports",
            image_url="http://example.com/image.jpg",
            is_featured=True,
            status="upcoming",
            ticket_types=[{"id": "ticket-1", "name": "VIP", "price": 500.00, "available": 100, "description": "VIP access"}],
            team_home={
                    "name": "Home Team",
                    "code": "HT",
                    "color": "#FF0000",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/ht.png",
                },
                team_away={
                    "name": "Away Team",
                    "code": "AT",
                    "color": "#0000FF",
                    "secondary_color": "#FFFFFF",
                    "logo": "https://example.com/at.png",
                },
        )

def test_customer_info_valid():
    customer_data = {"name": "John Doe", "email": "john@example.com", "phone": "+11234567890"}
    customer_info = CustomerInfo(**customer_data)
    assert customer_info.name == "John Doe"
    assert customer_info.email == "john@example.com"
    assert customer_info.phone == "+11234567890"


def test_customer_info_invalid_email():
    with pytest.raises(ValidationError):
        CustomerInfo(name="John Doe", email="invalid-email", phone="+11234567890")


def test_customer_info_invalid_phone():
    with pytest.raises(ValidationError):
        CustomerInfo(name="John Doe", email="john@example.com", phone="invalid")


def test_selected_ticket_valid():
    selected_ticket_data = {
        "ticket_type_id": "tkt-1",
        "quantity": 2,
        "price_per_ticket": 500.00,
    }
    selected_ticket = SelectedTicket(**selected_ticket_data)
    assert selected_ticket.ticket_type_id == "tkt-1"
    assert selected_ticket.quantity == 2
    assert selected_ticket.price_per_ticket == 500.00


def test_booking_schema_valid():
    booking_data = {
        "event_id": "evt-1",
        "customer_info": {"name": "John Doe", "email": "john@example.com", "phone": "+11234567890"},
        "selected_tickets": [
            {"ticket_type_id": "tkt-1", "quantity": 2, "price_per_ticket": 500.00}
        ],
    }
    booking = BookingSchema(**booking_data)
    assert booking.event_id == "evt-1"
    assert booking.customer_info.name == "John Doe"
    assert len(booking.selected_tickets) == 1
    assert booking.selected_tickets[0].quantity == 2


def test_booking_schema_invalid_event_id():
    with pytest.raises(ValidationError):
        BookingSchema(
            event_id=None,
            customer_info={"name": "John Doe", "email": "john@example.com", "phone": "+11234567890"},
            selected_tickets=[
                {"ticket_type_id": "tkt-1", "quantity": 2, "price_per_ticket": 500.00}
            ],
        )


def test_booking_schema_invalid_customer_info():
    with pytest.raises(ValidationError):
        BookingSchema(
            event_id="evt-1",
            customer_info=None,
            selected_tickets=[
                {"ticket_type_id": "tkt-1", "quantity": 2, "price_per_ticket": 500.00}
            ],
        )


def test_booking_schema_invalid_selected_tickets():
    with pytest.raises(ValidationError):
        BookingSchema(
            event_id="evt-1",
            customer_info={"name": "John Doe", "email": "john@example.com", "phone": "+11234567890"},
            selected_tickets=None,
        )


def test_user_in_db_valid():
    user_data = {
        "id": "user-1",
        "email": "user@example.com",
        "name": "User One",
        "hashed_password": "hashedpassword",
        "role": "user",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    user = UserInDB(**user_data)
    assert user.id == "user-1"
    assert user.email == "user@example.com"
    assert user.name == "User One"


def test_user_in_db_invalid_email():
    with pytest.raises(ValidationError):
        UserInDB(
            id="user-1",
            email="invalid-email",
            name="User One",
            hashed_password="hashedpassword",
            role="user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


def test_admin_in_db_valid():
    admin_data = {
        "id": "admin-1",
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": "hashedpassword",
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    admin = AdminInDB(**admin_data)
    assert admin.id == "admin-1"
    assert admin.username == "admin"
    assert admin.email == "admin@example.com"


def test_admin_in_db_invalid_email():
    with pytest.raises(ValidationError):
        AdminInDB(
            id="admin-1",
            username="admin",
            email="invalid-email",
            hashed_password="hashedpassword",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


def test_payment_settings_base_valid():
    payment_settings_data = {
        "merchant_name": "Eventia Payments",
        "vpa": "eventia@upi",
        "description": "UPI payments are enabled",
        "isPaymentEnabled": True,
        "payment_mode": "vpa",
    }
    payment_settings = PaymentSettingsBase(**payment_settings_data)
    assert payment_settings.merchant_name == "Eventia Payments"
    assert payment_settings.vpa == "eventia@upi"
    assert payment_settings.payment_mode == "vpa"


def test_payment_settings_base_invalid_payment_mode():
    with pytest.raises(ValidationError):
        PaymentSettingsBase(
            merchant_name="Eventia Payments",
            vpa="eventia@upi",
            description="UPI payments are enabled",
            isPaymentEnabled=True,
            payment_mode="invalid",
        )


def test_payment_settings_update_valid():
    payment_settings_update_data = {
        "merchant_name": "New Eventia Payments",
        "vpa": "neweventia@upi",
        "description": "New UPI payments are enabled",
        "isPaymentEnabled": False,
        "payment_mode": "qr_image",
        "qrImageUrl": "https://example.com/qr.png",
    }
    payment_settings_update = PaymentSettingsUpdate(**payment_settings_update_data)
    assert payment_settings_update.merchant_name == "New Eventia Payments"
    assert payment_settings_update.vpa == "neweventia@upi"
    assert payment_settings_update.isPaymentEnabled == False
    assert payment_settings_update.payment_mode == "qr_image"
    assert payment_settings_update.qrImageUrl == "https://example.com/qr.png"