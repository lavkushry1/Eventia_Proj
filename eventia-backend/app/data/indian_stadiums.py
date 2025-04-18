"""
Data models for major Indian stadiums.
This file contains detailed information about various Indian cricket and football stadiums
including their sections, pricing, capacity, and other relevant details.
"""

# Cricket Stadiums
NARENDRA_MODI_STADIUM = {
    "stadium_id": "narendra_modi_stadium",
    "name": "Narendra Modi Stadium",
    "city": "Ahmedabad",
    "country": "India",
    "capacity": 132000,
    "description": "The Narendra Modi Stadium (formerly known as Motera Stadium) is the largest cricket stadium in the world, with a seating capacity of 132,000 spectators.",
    "image_url": "/static/stadiums/narendra_modi_stadium.jpg",
    "ar_model_url": "/static/models/narendra_modi_stadium.glb",
    "is_active": True,
    "facilities": [
        {"name": "Parking", "icon": "car", "description": "Spacious parking for over 3,000 vehicles"},
        {"name": "Food Court", "icon": "utensils", "description": "Multiple food stalls with variety of cuisines"},
        {"name": "WiFi", "icon": "wifi", "description": "Free high-speed WiFi throughout the stadium"},
        {"name": "Medical Center", "icon": "first-aid", "description": "Fully equipped medical facility"},
        {"name": "ATMs", "icon": "credit-card", "description": "ATM machines available at multiple locations"}
    ],
    "sections": [
        {
            "section_id": "premium_pavilion",
            "name": "Premium Pavilion",
            "capacity": 5000,
            "price": 8000.00,
            "description": "Premium seating with the best view of the pitch and premium hospitality services",
            "availability": 5000,
            "color_code": "#FF2D55",
            "is_vip": True
        },
        {
            "section_id": "corporate_box",
            "name": "Corporate Box",
            "capacity": 2000,
            "price": 12000.00,
            "description": "Exclusive corporate boxes with private seating, dining and service",
            "availability": 2000,
            "color_code": "#AF52DE",
            "is_vip": True
        },
        {
            "section_id": "east_upper",
            "name": "East Upper Tier",
            "capacity": 25000,
            "price": 3000.00,
            "description": "Upper tier seating on the eastern side of the stadium",
            "availability": 25000,
            "color_code": "#5AC8FA",
            "is_vip": False
        },
        {
            "section_id": "east_lower",
            "name": "East Lower Tier",
            "capacity": 25000,
            "price": 2000.00,
            "description": "Lower tier seating on the eastern side of the stadium",
            "availability": 25000,
            "color_code": "#34C759",
            "is_vip": False
        },
        {
            "section_id": "west_upper",
            "name": "West Upper Tier",
            "capacity": 25000,
            "price": 3000.00,
            "description": "Upper tier seating on the western side of the stadium",
            "availability": 25000,
            "color_code": "#5AC8FA",
            "is_vip": False
        },
        {
            "section_id": "west_lower",
            "name": "West Lower Tier",
            "capacity": 25000,
            "price": 2000.00,
            "description": "Lower tier seating on the western side of the stadium",
            "availability": 25000,
            "color_code": "#34C759",
            "is_vip": False
        },
        {
            "section_id": "north_stand",
            "name": "North Stand",
            "capacity": 12500,
            "price": 1500.00,
            "description": "Seating in the north stand",
            "availability": 12500,
            "color_code": "#FFCC00",
            "is_vip": False
        },
        {
            "section_id": "south_stand",
            "name": "South Stand",
            "capacity": 12500,
            "price": 1500.00,
            "description": "Seating in the south stand",
            "availability": 12500,
            "color_code": "#FFCC00",
            "is_vip": False
        }
    ]
}

EDEN_GARDENS = {
    "stadium_id": "eden_gardens",
    "name": "Eden Gardens",
    "city": "Kolkata",
    "country": "India",
    "capacity": 68000,
    "description": "Eden Gardens is one of the oldest and most iconic cricket stadiums in India, known for its passionate crowd and historic matches.",
    "image_url": "/static/stadiums/eden_gardens.jpg",
    "ar_model_url": "/static/models/eden_gardens.glb",
    "is_active": True,
    "facilities": [
        {"name": "Parking", "icon": "car", "description": "Parking facility available"},
        {"name": "Food Court", "icon": "utensils", "description": "Multiple food stalls with Bengali cuisine specialty"},
        {"name": "Museum", "icon": "landmark", "description": "Cricket museum showcasing the stadium's rich history"},
        {"name": "Medical Center", "icon": "first-aid", "description": "Medical facility for emergencies"}
    ],
    "sections": [
        {
            "section_id": "a_block",
            "name": "A Block",
            "capacity": 10000,
            "price": 5000.00,
            "description": "Premium seating with excellent view",
            "availability": 10000,
            "color_code": "#FF2D55",
            "is_vip": True
        },
        {
            "section_id": "b_block",
            "name": "B Block",
            "capacity": 15000,
            "price": 3000.00,
            "description": "Good seating with great view of the pitch",
            "availability": 15000,
            "color_code": "#5AC8FA",
            "is_vip": False
        },
        {
            "section_id": "c_block",
            "name": "C Block",
            "capacity": 15000,
            "price": 2000.00,
            "description": "Standard seating",
            "availability": 15000,
            "color_code": "#34C759",
            "is_vip": False
        },
        {
            "section_id": "d_block",
            "name": "D Block",
            "capacity": 15000,
            "price": 1500.00,
            "description": "Economy seating",
            "availability": 15000,
            "color_code": "#FFCC00",
            "is_vip": False
        },
        {
            "section_id": "corporate_box",
            "name": "Corporate Box",
            "capacity": 3000,
            "price": 8000.00,
            "description": "Exclusive corporate boxes with premium services",
            "availability": 3000,
            "color_code": "#AF52DE",
            "is_vip": True
        },
        {
            "section_id": "club_house",
            "name": "Club House",
            "capacity": 10000,
            "price": 4000.00,
            "description": "Club house seating with additional amenities",
            "availability": 10000,
            "color_code": "#FF9500",
            "is_vip": True
        }
    ]
}

WANKHEDE_STADIUM = {
    "stadium_id": "wankhede_stadium",
    "name": "Wankhede Stadium",
    "city": "Mumbai",
    "country": "India",
    "capacity": 33000,
    "description": "Wankhede Stadium is a cricket stadium in Mumbai, India. It is home to Mumbai Cricket Association and the venue for international cricket matches.",
    "image_url": "/static/stadiums/wankhede_stadium.jpg",
    "ar_model_url": "/static/models/wankhede_stadium.glb",
    "is_active": True,
    "facilities": [
        {"name": "Parking", "icon": "car", "description": "Limited parking available"},
        {"name": "Food Court", "icon": "utensils", "description": "Food stalls with local and international cuisine"},
        {"name": "WiFi", "icon": "wifi", "description": "Free WiFi in premium areas"},
        {"name": "ATMs", "icon": "credit-card", "description": "ATM facilities available"}
    ],
    "sections": [
        {
            "section_id": "north_stand",
            "name": "North Stand",
            "capacity": 8000,
            "price": 4000.00,
            "description": "Premium seating in the north stand",
            "availability": 8000,
            "color_code": "#FF2D55",
            "is_vip": True
        },
        {
            "section_id": "sunil_gavaskar_stand",
            "name": "Sunil Gavaskar Stand",
            "capacity": 5000,
            "price": 3500.00,
            "description": "Named after the legendary cricketer with excellent view",
            "availability": 5000,
            "color_code": "#5AC8FA",
            "is_vip": False
        },
        {
            "section_id": "sachin_tendulkar_stand",
            "name": "Sachin Tendulkar Stand",
            "capacity": 8000,
            "price": 3000.00,
            "description": "Named after Mumbai's cricketing icon",
            "availability": 8000,
            "color_code": "#34C759",
            "is_vip": False
        },
        {
            "section_id": "vijay_merchant_stand",
            "name": "Vijay Merchant Stand",
            "capacity": 7000,
            "price": 2500.00,
            "description": "Good viewing position",
            "availability": 7000,
            "color_code": "#FFCC00",
            "is_vip": False
        },
        {
            "section_id": "divecha_stand",
            "name": "Divecha Stand",
            "capacity": 5000,
            "price": 2000.00,
            "description": "Standard seating",
            "availability": 5000,
            "color_code": "#FF9500",
            "is_vip": False
        }
    ]
}

# Football Stadiums
JAWAHARLAL_NEHRU_STADIUM = {
    "stadium_id": "jawaharlal_nehru_stadium",
    "name": "Jawaharlal Nehru Stadium",
    "city": "New Delhi",
    "country": "India",
    "capacity": 60000,
    "description": "Jawaharlal Nehru Stadium is a multi-purpose sports venue located in New Delhi, India. It is the main venue for football events in Delhi.",
    "image_url": "/static/stadiums/jawaharlal_nehru_stadium.jpg",
    "ar_model_url": "/static/models/jawaharlal_nehru_stadium.glb",
    "is_active": True,
    "facilities": [
        {"name": "Parking", "icon": "car", "description": "Large parking area available"},
        {"name": "Food Court", "icon": "utensils", "description": "Multiple food and beverage options"},
        {"name": "Metro Access", "icon": "train", "description": "Direct access to Jawaharlal Nehru Stadium metro station"},
        {"name": "Medical Facility", "icon": "first-aid", "description": "On-site medical center"}
    ],
    "sections": [
        {
            "section_id": "vip_box",
            "name": "VIP Box",
            "capacity": 500,
            "price": 10000.00,
            "description": "Exclusive VIP boxes with premium services",
            "availability": 500,
            "color_code": "#AF52DE",
            "is_vip": True
        },
        {
            "section_id": "premium_east",
            "name": "Premium East",
            "capacity": 10000,
            "price": 5000.00,
            "description": "Premium seating on the eastern side",
            "availability": 10000,
            "color_code": "#FF2D55",
            "is_vip": True
        },
        {
            "section_id": "premium_west",
            "name": "Premium West",
            "capacity": 10000,
            "price": 5000.00,
            "description": "Premium seating on the western side",
            "availability": 10000,
            "color_code": "#FF2D55",
            "is_vip": True
        },
        {
            "section_id": "north_stand",
            "name": "North Stand",
            "capacity": 15000,
            "price": 2000.00,
            "description": "Seating in the north stand",
            "availability": 15000,
            "color_code": "#34C759",
            "is_vip": False
        },
        {
            "section_id": "south_stand",
            "name": "South Stand",
            "capacity": 15000,
            "price": 2000.00,
            "description": "Seating in the south stand",
            "availability": 15000,
            "color_code": "#34C759",
            "is_vip": False
        },
        {
            "section_id": "general",
            "name": "General",
            "capacity": 9500,
            "price": 1000.00,
            "description": "General admission seating",
            "availability": 9500,
            "color_code": "#FFCC00",
            "is_vip": False
        }
    ]
}

SALT_LAKE_STADIUM = {
    "stadium_id": "salt_lake_stadium",
    "name": "Salt Lake Stadium",
    "city": "Kolkata",
    "country": "India",
    "capacity": 85000,
    "description": "Salt Lake Stadium, officially known as Vivekananda Yuba Bharati Krirangan, is a multi-purpose stadium in Kolkata, India. It is the largest football stadium in India.",
    "image_url": "/static/stadiums/salt_lake_stadium.jpg",
    "ar_model_url": "/static/models/salt_lake_stadium.glb",
    "is_active": True,
    "facilities": [
        {"name": "Parking", "icon": "car", "description": "Ample parking space"},
        {"name": "Food Court", "icon": "utensils", "description": "Various food stalls"},
        {"name": "Training Field", "icon": "futbol", "description": "Adjacent training fields"},
        {"name": "ATMs", "icon": "credit-card", "description": "ATM machines available"}
    ],
    "sections": [
        {
            "section_id": "vip_gallery",
            "name": "VIP Gallery",
            "capacity": 5000,
            "price": 8000.00,
            "description": "Exclusive VIP seating with the best view",
            "availability": 5000,
            "color_code": "#FF2D55",
            "is_vip": True
        },
        {
            "section_id": "east_gallery",
            "name": "East Gallery",
            "capacity": 20000,
            "price": 3000.00,
            "description": "Seating in the east gallery",
            "availability": 20000,
            "color_code": "#5AC8FA",
            "is_vip": False
        },
        {
            "section_id": "west_gallery",
            "name": "West Gallery",
            "capacity": 20000,
            "price": 3000.00,
            "description": "Seating in the west gallery",
            "availability": 20000,
            "color_code": "#5AC8FA",
            "is_vip": False
        },
        {
            "section_id": "north_gallery",
            "name": "North Gallery",
            "capacity": 20000,
            "price": 2000.00,
            "description": "Seating in the north gallery",
            "availability": 20000,
            "color_code": "#34C759",
            "is_vip": False
        },
        {
            "section_id": "south_gallery",
            "name": "South Gallery",
            "capacity": 20000,
            "price": 2000.00,
            "description": "Seating in the south gallery",
            "availability": 20000,
            "color_code": "#34C759",
            "is_vip": False
        }
    ]
}

# List of all stadiums
INDIAN_STADIUMS = [
    NARENDRA_MODI_STADIUM,
    EDEN_GARDENS,
    WANKHEDE_STADIUM,
    JAWAHARLAL_NEHRU_STADIUM,
    SALT_LAKE_STADIUM
] 