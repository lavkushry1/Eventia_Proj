# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-13 18:34:45
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-14 00:24:14
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import logging
import sys
import os
import time
from utils.middleware import add_correlation_id_middleware, log_execution_time
from utils.logger import logger
from utils.metrics import metrics
from utils.memory_profiler import memory_profiler, profile_memory
import base64
import pymongo
import re
import hashlib
import shutil
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId  # needed for update endpoints

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/eventia')
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client.get_database()
    logger.info(f"Connected to MongoDB: {MONGO_URI}")
    
    # Initialize default UPI settings if not exist
    if db.settings.count_documents({"type": "upi_settings"}) == 0:
        db.settings.insert_one({
            "type": "upi_settings",
            "merchant_name": "Eventia Tickets",
            "vpa": "eventia@upi",
            "description": "Official payment account for Eventia ticket purchases",
            "updated_at": datetime.now()
        })
        logger.info("Initialized default UPI settings")
        
    # Create indexes for better query performance
    db.bookings.create_index("booking_id")
    db.bookings.create_index("status")
    db.bookings.create_index("created_at")
    db.events.create_index("id")
    logger.info("Created database indexes")
    
except Exception as e:
    logger.error(f"Could not connect to MongoDB: {e}")
    sys.exit(1)

# Admin token for authentication - in production, use a strong, randomly generated token
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'supersecuretoken123')

# Log that the token is configured, but only show the first few characters for security
logger.info(f"Admin token configured (first 4 chars): {ADMIN_TOKEN[:4]}***")

# Helper function to validate Basic Auth credentials
def check_auth(authorization_header):
    if not authorization_header or not authorization_header.startswith('Basic '):
        return False
    
    try:
        # Extract and decode the base64 credentials
        encoded_credentials = authorization_header[6:]  # Remove 'Basic '
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':')
        
        # Simple check: password should match ADMIN_TOKEN
        # Username can be anything in this implementation
        return password == ADMIN_TOKEN
    except Exception as e:
        logging.error(f"Auth error: {str(e)}")
        return False

# Helper function to validate Bearer token
def check_bearer_token(authorization_header):
    if not authorization_header or not authorization_header.startswith('Bearer '):
        return False
    
    try:
        # Extract the token
        token = authorization_header.split(' ')[1]
        
        # Simple check: token should match ADMIN_TOKEN
        return token == ADMIN_TOKEN
    except Exception as e:
        logging.error(f"Bearer token auth error: {str(e)}")
        return False

# Auth endpoint for Nginx auth_request
@app.route('/auth', methods=['GET'])
def auth():
    auth_header = request.headers.get('Authorization')
    
    if check_auth(auth_header):
        return '', 200
    else:
        return 'Unauthorized', 401

# Add dedicated admin login endpoint
@app.route('/api/admin/login', methods=['POST'])
@log_execution_time
def admin_login():
    try:
        data = request.json
        token = data.get('token')
        username = data.get('username')
        password = data.get('password')
        
        # Check if it's a token-based auth
        if token:
            if token == ADMIN_TOKEN:
                logger.info("Successful admin login via token")
                return jsonify({
                    "status": "success",
                    "message": "Admin login successful",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                logger.warning("Failed admin login attempt via token")
                return jsonify({"error": "Invalid admin token"}), 401
        
        # Check if it's username/password auth
        elif username and password:
            # Find admin in database
            admin = db.admin_users.find_one({"username": username})
            
            if not admin:
                logger.warning(f"Failed admin login attempt: username {username} not found")
                return jsonify({"error": "Invalid username or password"}), 401
            
            # Import and use password verification
            from app.utils.password import verify_password
            
            # Verify password
            if verify_password(admin['hashed_password'], password):
                logger.info(f"Successful admin login for user: {username}")
                
                # Generate a session token
                import uuid
                session_token = str(uuid.uuid4())
                
                # Store session token in db with expiry
                db.admin_sessions.insert_one({
                    "token": session_token,
                    "admin_id": str(admin['_id']),
                    "created_at": datetime.now(),
                    "expires_at": datetime.now() + timedelta(days=1)
                })
                
                return jsonify({
                    "status": "success",
                    "message": "Admin login successful",
                    "token": session_token,
                    "admin": {
                        "id": str(admin['_id']),
                        "username": admin['username'],
                        "email": admin['email']
                    },
                    "timestamp": datetime.now().isoformat()
                })
            else:
                logger.warning(f"Failed admin login attempt: invalid password for {username}")
                return jsonify({"error": "Invalid username or password"}), 401
        else:
            logger.warning("Admin login attempt with missing credentials")
            return jsonify({"error": "Admin credentials are required"}), 400
    except Exception as e:
        logger.error(f"Error in admin login: {str(e)}", exc_info=True)
        return jsonify({"error": f"Admin login failed: {str(e)}"}), 500

# Add after app definition
add_correlation_id_middleware(app)

# API Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to Eventia API"})

# Add health check endpoint
@app.route('/health', methods=['GET'])
@log_execution_time
def health_check():
    """Health check endpoint."""
    try:
        # Add memory stats to health check
        memory_stats = memory_profiler.get_memory_stats()
        
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "memory": memory_stats
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "reason": f"Health check failed: {str(e)}"
        }), 500

@app.route('/api/events', methods=['GET'])
@log_execution_time
def get_events():
    try:
        category = request.args.get('category')
        query = {}
        if category:
            query["category"] = category
            
        events_cursor = db.events.find(query)
        events_list = list(events_cursor)
        
        # Convert ObjectId to string and format response to match frontend expectations
        formatted_events = []
        for event in events_list:
            # Convert MongoDB _id to id
            event['id'] = str(event.pop('_id')) if '_id' in event else f"evt_{len(formatted_events) + 1}"
            
            # Ensure all required fields exist with proper naming
            formatted_event = {
                "id": event.get('id'),
                "title": event.get('name', 'Untitled Event'),
                "description": event.get('description', ''),
                "date": event.get('date', datetime.now().strftime("%Y-%m-%d")),
                "time": event.get('time', '19:30'),
                "venue": event.get('venue', 'TBD'),
                "ticket_price": event.get('price', 0),
                "tickets_available": event.get('availability', 0),
                "image_url": event.get('image_url', f"https://picsum.photos/800/450?random={len(formatted_events) + 1}"),
                "category": event.get('category', 'General'),
                "is_featured": event.get('is_featured', False),
                "status": event.get('status', 'available'),
            }
            
            # Add team data if it exists
            if 'teams' in event:
                formatted_event["team_home"] = {
                    "name": event['teams'].get('home', {}).get('name', ''),
                    "logo": event['teams'].get('home', {}).get('code', '').lower(),
                    "primary_color": event['teams'].get('home', {}).get('color', '#000000'),
                    "secondary_color": event['teams'].get('home', {}).get('secondary_color', '#FFFFFF')
                }
                formatted_event["team_away"] = {
                    "name": event['teams'].get('away', {}).get('name', ''),
                    "logo": event['teams'].get('away', {}).get('code', '').lower(),
                    "primary_color": event['teams'].get('away', {}).get('color', '#000000'),
                    "secondary_color": event['teams'].get('away', {}).get('secondary_color', '#FFFFFF')
                }
            
            # Include ticket types if available
            if 'ticketTypes' in event:
                formatted_event["ticket_types"] = []
                for ticket_type in event['ticketTypes']:
                    formatted_ticket = {
                        "id": str(ticket_type.get('id', f"tkt_{len(formatted_event['ticket_types']) + 1}")),
                        "name": ticket_type.get('name', 'Regular'),
                        "price": ticket_type.get('price', formatted_event['ticket_price']),
                        "available": ticket_type.get('available', 0),
                        "description": ticket_type.get('description', '')
                    }
                    formatted_event["ticket_types"].append(formatted_ticket)
            
            formatted_events.append(formatted_event)
        
        return jsonify(formatted_events)
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/events/<event_id>')
@log_execution_time
def get_event(event_id):
    try:
        # Log the requested event_id for debugging
        logger.info(f"Fetching event with ID: {event_id}")
        
        # Initialize event as None
        event = None
        
        # First try: Find by string ID exactly as provided
        event = db.events.find_one({"_id": event_id})
        logger.info(f"Searched by exact string _id: {event_id}, found: {event is not None}")
        
        # Second try: Try to find by MongoDB ObjectId if the ID format is valid
        if not event:
            try:
                from bson.objectid import ObjectId
                if ObjectId.is_valid(event_id):
                    event = db.events.find_one({"_id": ObjectId(event_id)})
                    logger.info(f"Searched by ObjectId: {event_id}, found: {event is not None}")
            except Exception as oid_error:
                logger.warning(f"Error when searching by ObjectId: {str(oid_error)}")
        
        # Third try: Try by 'id' field
        if not event:
            event = db.events.find_one({"id": event_id})
            logger.info(f"Searched by id field: {event_id}, found: {event is not None}")
        
        if not event:
            logger.warning(f"Event not found with ID: {event_id}")
            return jsonify({"error": f"Event not found with ID: {event_id}"}), 404
        
        # Log found event structure
        logger.info(f"Found event with ID: {event_id}, structure: {list(event.keys())}")
        
        # Format the event response
        if '_id' in event:
            from bson.objectid import ObjectId
            if isinstance(event['_id'], ObjectId):
                event['id'] = str(event.pop('_id'))
            else:
                event['id'] = event.pop('_id')
                
        # Ensure all required fields exist with proper naming
        formatted_event = {
            "id": event.get('id', f"evt_unknown"),
            "title": event.get('name', 'Untitled Event'),
            "description": event.get('description', ''),
            "date": event.get('date', datetime.now().strftime("%Y-%m-%d")),
            "time": event.get('time', '19:30'),
            "venue": event.get('venue', 'TBD'),
            "ticket_price": event.get('price', 0),
            "tickets_available": event.get('availability', 0),
            "image_url": event.get('image_url', f"https://picsum.photos/800/450?random=1"),
            "category": event.get('category', 'General'),
            "is_featured": event.get('is_featured', False),
            "status": event.get('status', 'available'),
        }
        
        # Add team data if it exists
        if 'teams' in event:
            try:
                formatted_event["team_home"] = {
                    "name": event['teams'].get('home', {}).get('name', ''),
                    "logo": event['teams'].get('home', {}).get('code', '').lower(),
                    "primary_color": event['teams'].get('home', {}).get('color', '#000000'),
                    "secondary_color": event['teams'].get('home', {}).get('secondary_color', '#FFFFFF')
                }
                formatted_event["team_away"] = {
                    "name": event['teams'].get('away', {}).get('name', ''),
                    "logo": event['teams'].get('away', {}).get('code', '').lower(),
                    "primary_color": event['teams'].get('away', {}).get('color', '#000000'),
                    "secondary_color": event['teams'].get('away', {}).get('secondary_color', '#FFFFFF')
                }
                logger.info(f"Added team data to event response for {event_id}")
            except Exception as team_error:
                logger.error(f"Error processing team data: {str(team_error)}")
        
        # Include ticket types if available
        if 'ticketTypes' in event:
            formatted_event["ticket_types"] = []
            try:
                for ticket_type in event['ticketTypes']:
                    formatted_ticket = {
                        "id": str(ticket_type.get('id', f"tkt_{len(formatted_event['ticket_types']) + 1}")),
                        "name": ticket_type.get('name', 'Regular'),
                        "price": ticket_type.get('price', formatted_event['ticket_price']),
                        "available": ticket_type.get('available', 0),
                        "description": ticket_type.get('description', '')
                    }
                    formatted_event["ticket_types"].append(formatted_ticket)
                logger.info(f"Added {len(formatted_event['ticket_types'])} ticket types to event response")
            except Exception as ticket_error:
                logger.error(f"Error processing ticket types: {str(ticket_error)}")
                # Fallback to default ticket type
                formatted_event["ticket_types"] = [{
                    "id": f"tkt_default_{event_id}",
                    "name": "Standard",
                    "price": formatted_event["ticket_price"],
                    "available": formatted_event["tickets_available"],
                    "description": "Standard ticket"
                }]
        else:
            # Create default ticket type if none exists
            formatted_event["ticket_types"] = [{
                "id": f"tkt_default_{event_id}",
                "name": "Standard",
                "price": formatted_event["ticket_price"],
                "available": formatted_event["tickets_available"],
                "description": "Standard ticket"
            }]
            logger.info(f"Created default ticket type for event {event_id}")
        
        logger.info(f"Successfully prepared event response for {event_id}")
        return jsonify(formatted_event)
    except Exception as e:
        logger.error(f"Error fetching event {event_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch event: {str(e)}"}), 500

@app.route('/api/bookings', methods=['POST'])
@log_execution_time
@profile_memory
def create_booking():
    try:
        data = request.json
        
        # Find event
        event_id = data.get("event_id")
        try:
            from bson.objectid import ObjectId
            if ObjectId.is_valid(event_id):
                event = db.events.find_one({"_id": ObjectId(event_id)})
            else:
                event = db.events.find_one({"id": event_id})
        except:
            event = db.events.find_one({"id": event_id})
        
        if not event:
            return jsonify({"error": "Event not found"}), 404
        
        # Check tickets availability
        quantity = data.get("quantity", 1)
        availability = event.get("availability", 0)
        if availability < quantity:
            return jsonify({"error": "Not enough tickets available"}), 400
        
        # Create booking
        booking_id = f"booking_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        total_amount = event.get("price", 0) * quantity
        
        new_booking = {
            "booking_id": booking_id,
            "event_id": event_id,
            "quantity": quantity,
            "customer_info": data.get("customer_info", {}),
            "status": "pending",
            "total_amount": total_amount,
            "created_at": datetime.now()
        }
        
        # Insert booking into MongoDB
        db.bookings.insert_one(new_booking)
        
        # Update event tickets (decrease availability)
        db.events.update_one(
            {"_id": event["_id"] if "_id" in event else event["id"]},
            {"$inc": {"availability": -quantity}}
        )
        
        return jsonify({
            "booking_id": booking_id,
            "status": "pending",
            "total_amount": total_amount
        })
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/verify-payment', methods=['POST'])
@log_execution_time
@profile_memory
def verify_payment():
    try:
        data = request.json
        booking_id = data.get("booking_id")
        utr = data.get("utr", "")
        
        # Validate UTR format - should be 10-23 alphanumeric characters
        if not re.match(r'^[A-Za-z0-9]{10,23}$', utr):
            logger.warning(f"Invalid UTR format: {utr}")
            return jsonify({"error": "Invalid UTR format. Please enter the correct UTR number from your payment confirmation."}), 400
        
        # Find booking
        booking = db.bookings.find_one({"booking_id": booking_id})
        
        if not booking:
            logger.warning(f"Booking not found for booking_id: {booking_id}")
            return jsonify({"error": "Booking not found"}), 404
        
        # Check if booking is expired (older than 30 minutes)
        booking_time = booking.get("created_at", datetime.now())
        if isinstance(booking_time, str):
            try:
                booking_time = datetime.fromisoformat(booking_time.replace('Z', '+00:00'))
            except ValueError:
                booking_time = datetime.now()
                
        time_diff = datetime.now() - booking_time
        if time_diff.total_seconds() > 1800:  # 30 minutes
            # Mark as expired and release inventory
            db.bookings.update_one(
                {"booking_id": booking_id},
                {"$set": {"status": "expired"}}
            )
            
            # Update event tickets (increase availability)
            event_id = booking.get("event_id")
            quantity = booking.get("quantity", 1)
            
            if event_id:
                try:
                    from bson.objectid import ObjectId
                    if ObjectId.is_valid(event_id):
                        db.events.update_one(
                            {"_id": ObjectId(event_id)},
                            {"$inc": {"availability": quantity}}
                        )
                    else:
                        db.events.update_one(
                            {"id": event_id},
                            {"$inc": {"availability": quantity}}
                        )
                except Exception as e:
                    logger.error(f"Error releasing inventory: {e}")
            
            logger.warning(f"Booking {booking_id} expired (created {time_diff.total_seconds()/60:.1f} minutes ago)")
            return jsonify({"error": "This booking has expired. Please create a new booking."}), 400
        
        # Log the payment verification attempt
        logger.info(f"Verifying payment for booking {booking_id} with UTR: {utr}")
        
        # Update booking status
        db.bookings.update_one(
            {"booking_id": booking_id},
            {"$set": {
                "utr": utr,
                "status": "confirmed",
                "payment_verified_at": datetime.now()
            }}
        )
        
        # Generate ticket ID - use a more unique format
        # Combine booking ID with a short hash for more uniqueness
        short_hash = hashlib.md5(f"{booking_id}-{utr}".encode()).hexdigest()[:6]
        ticket_id = f"TKT-{booking_id[-5:]}-{short_hash}"
        
        # Update booking with ticket ID
        db.bookings.update_one(
            {"booking_id": booking_id},
            {"$set": {"ticket_id": ticket_id}}
        )
        
        logger.info(f"Payment verified for booking {booking_id}. Ticket ID: {ticket_id}")
        
        return jsonify({
            "status": "success",
            "ticket_id": ticket_id
        })
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        return jsonify({"error": str(e)}), 500

# New UPI payment settings endpoints
@app.route('/api/payment-settings', methods=['GET'])
@log_execution_time
def get_payment_settings():
    try:
        # Get UPI settings from database
        settings = db.settings.find_one({"type": "upi_settings"})
        
        if not settings:
            # Create default settings if none exist
            default_settings = {
                "type": "upi_settings",
                "merchant_name": "Eventia Tickets",
                "vpa": "eventia@upi",
                "description": "Official payment account for Eventia ticket purchases",
                "payment_mode": "vpa",
                "qrImageUrl": None,
                "updated_at": datetime.now()
            }
            db.settings.insert_one(default_settings)
            settings = default_settings
            logger.info("Created default payment settings")
        
        # Remove MongoDB ID from response
        if "_id" in settings:
            settings.pop("_id")
        
        # Format date
        if "updated_at" in settings:
            settings["updated_at"] = settings["updated_at"].isoformat()
        
        # Format the response to match the frontend expectations
        formatted_settings = {
            "isPaymentEnabled": True,
            "merchant_name": settings.get("merchant_name", "Eventia Tickets"),
            "vpa": settings.get("vpa", "eventia@upi"),
            "vpaAddress": settings.get("vpa", "eventia@upi"),  # For frontend compatibility
            "description": settings.get("description", ""),
            "payment_mode": settings.get("payment_mode", "vpa"),
            "qrImageUrl": settings.get("qrImageUrl", None),
            "updated_at": settings.get("updated_at", datetime.now().isoformat())
        }
        
        logger.info("Returning payment settings: " + json.dumps(formatted_settings))
        return jsonify(formatted_settings)
    except Exception as e:
        logger.error(f"Error fetching UPI settings: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/payment-settings', methods=['PUT'])
@log_execution_time
def update_payment_settings():
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not check_bearer_token(auth_header):
            logger.warning("Unauthorized attempt to update payment settings")
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.json
        required_fields = ["merchant_name", "vpa"]
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field in payment settings update: {field}")
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Get existing settings
        existing_settings = db.settings.find_one({"type": "upi_settings"}) or {}
        
        # Update settings
        update_data = {
            "merchant_name": data["merchant_name"],
            "vpa": data["vpa"],
            "description": data.get("description", ""),
            "payment_mode": data.get("payment_mode", "vpa"),
            "updated_at": datetime.now()
        }
        
        # Update or insert settings
        if existing_settings:
            db.settings.update_one(
                {"type": "upi_settings"},
                {"$set": update_data}
            )
        else:
            update_data["type"] = "upi_settings"
            db.settings.insert_one(update_data)
        
        # Fetch updated settings to return
        updated_settings = db.settings.find_one({"type": "upi_settings"})
        if "_id" in updated_settings:
            updated_settings.pop("_id")
        if "updated_at" in updated_settings:
            updated_settings["updated_at"] = updated_settings["updated_at"].isoformat()
            
        # Format for response
        formatted_response = {
            "status": "success",
            "message": "Payment settings updated successfully",
            "settings": {
                "isPaymentEnabled": True,
                "merchant_name": updated_settings.get("merchant_name", ""),
                "vpa": updated_settings.get("vpa", ""),
                "vpaAddress": updated_settings.get("vpa", ""),  # For frontend compatibility
                "description": updated_settings.get("description", ""),
                "payment_mode": updated_settings.get("payment_mode", "vpa"),
                "qrImageUrl": updated_settings.get("qrImageUrl", None),
                "updated_at": updated_settings.get("updated_at", datetime.now().isoformat())
            }
        }
        
        logger.info(f"Payment settings updated successfully: {json.dumps(formatted_response['settings'])}")
        return jsonify(formatted_response)
    except Exception as e:
        logger.error(f"Error updating payment settings: {e}")
        return jsonify({"error": str(e)}), 500

# Add a new endpoint for QR image upload
@app.route('/api/admin/settings/payment', methods=['POST'])
@log_execution_time
def update_payment_settings_with_image():
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        if token != ADMIN_TOKEN:
            return jsonify({"error": "Invalid admin token"}), 401
        
        # Get form data
        merchant_name = request.form.get('merchant_name', '')
        vpa = request.form.get('vpa', '')
        description = request.form.get('description', '')
        payment_mode = request.form.get('payment_mode', 'vpa')
        
        if not merchant_name or not vpa:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Prepare settings document
        update_data = {
            "merchant_name": merchant_name,
            "vpa": vpa,
            "description": description,
            "payment_mode": payment_mode,
            "updated_at": datetime.now()
        }
        
        # Handle QR image upload if provided
        if 'qrImage' in request.files:
            qr_image = request.files['qrImage']
            
            if qr_image and qr_image.filename:
                logger.info(f"Processing QR image upload: {qr_image.filename}")
                
                # Validate file type
                if not qr_image.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    logger.warning("Invalid file type")
                    return jsonify({
                        "error": "Only JPG and PNG images are allowed"
                    }), 400
                
                # Generate unique filename
                filename = f"payment_qr_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(qr_image.filename)[1]}"
                file_path = os.path.join("static/uploads", secure_filename(filename))
                
                # Create uploads directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Save file
                qr_image.save(file_path)
                logger.info(f"Saved QR image to {file_path}")
                
                # Set QR image URL
                relative_path = f"/static/uploads/{secure_filename(filename)}"
                update_data["qrImageUrl"] = relative_path
                logger.info(f"Set qrImageUrl to {relative_path}")
        
        # Update settings in database
        db.settings.update_one(
            {"type": "upi_settings"},
            {"$set": update_data},
            upsert=True
        )
        
        # Format date for response
        response_data = update_data.copy()
        response_data["updated_at"] = update_data["updated_at"].isoformat()
        
        return jsonify({
            "status": "success",
            "message": "Payment settings updated successfully",
            "settings": response_data
        })
    except Exception as e:
        logger.error(f"Error updating payment settings with image: {str(e)}", exc_info=True)
        return jsonify({
            "error": f"Failed to update payment settings: {str(e)}"
        }), 500

# Add metrics endpoint
@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Prometheus metrics endpoint."""
    return metrics.get_prometheus_metrics(), 200, {'Content-Type': 'text/plain'}

@app.route('/api/admin/analytics', methods=['GET'])
@log_execution_time
def get_admin_analytics():
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        if token != ADMIN_TOKEN:
            return jsonify({"error": "Invalid admin token"}), 401
            
        # Get analytics data
        total_events = db.events.count_documents({})
        total_bookings = db.bookings.count_documents({})
        confirmed_bookings = db.bookings.count_documents({"status": "confirmed"})
        pending_bookings = db.bookings.count_documents({"status": "pending"})
        total_revenue = 0
        
        # Calculate revenue from confirmed bookings
        confirmed_bookings_data = list(db.bookings.find({"status": "confirmed"}))
        for booking in confirmed_bookings_data:
            total_revenue += booking.get("total_amount", 0)
            
        # Get recent bookings
        recent_bookings = list(db.bookings.find().sort("created_at", -1).limit(5))
        formatted_recent_bookings = []
        
        for booking in recent_bookings:
            # Convert MongoDB _id to string
            booking['id'] = str(booking.pop('_id')) if '_id' in booking else booking.get('booking_id')
            
            # Format dates
            if 'created_at' in booking and isinstance(booking['created_at'], datetime):
                booking['created_at'] = booking['created_at'].isoformat()
                
            formatted_recent_bookings.append(booking)
            
        # Get popular events (most booked)
        pipeline = [
            {"$group": {"_id": "$event_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        popular_events_data = list(db.bookings.aggregate(pipeline))
        popular_events = []
        
        for event_data in popular_events_data:
            event_id = event_data['_id']
            count = event_data['count']
            
            # Get event details
            try:
                from bson.objectid import ObjectId
                if ObjectId.is_valid(event_id):
                    event = db.events.find_one({"_id": ObjectId(event_id)})
                else:
                    event = db.events.find_one({"id": event_id})
            except:
                event = db.events.find_one({"id": event_id})
                
            if event:
                popular_events.append({
                    "id": event_id,
                    "title": event.get('name', 'Unknown Event'),
                    "bookings_count": count
                })
                
        return jsonify({
            "total_events": total_events,
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "pending_bookings": pending_bookings,
            "total_revenue": total_revenue,
            "recent_bookings": formatted_recent_bookings,
            "popular_events": popular_events
        })
        
    except Exception as e:
        logger.error(f"Error fetching admin analytics: {e}")
        return jsonify({"error": str(e)}), 500

# Scheduled task to clean up expired bookings
@app.route('/api/admin/cleanup-expired', methods=['POST'])
@log_execution_time
def cleanup_expired_bookings():
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        if token != ADMIN_TOKEN:
            return jsonify({"error": "Invalid admin token"}), 401
            
        # Find bookings older than 30 minutes that are still pending
        thirty_mins_ago = datetime.now() - timedelta(minutes=30)
        
        # Find expired bookings
        expired_bookings = list(db.bookings.find({
            "status": "pending",
            "created_at": {"$lt": thirty_mins_ago}
        }))
        
        expired_count = 0
        inventory_updated = 0
        
        # Process each expired booking
        for booking in expired_bookings:
            booking_id = booking.get("booking_id")
            event_id = booking.get("event_id")
            quantity = booking.get("quantity", 1)
            
            # Update the booking status
            db.bookings.update_one(
                {"booking_id": booking_id},
                {"$set": {"status": "expired"}}
            )
            expired_count += 1
            
            # Release ticket inventory
            if event_id:
                try:
                    from bson.objectid import ObjectId
                    if ObjectId.is_valid(event_id):
                        result = db.events.update_one(
                            {"_id": ObjectId(event_id)},
                            {"$inc": {"availability": quantity}}
                        )
                    else:
                        result = db.events.update_one(
                            {"id": event_id},
                            {"$inc": {"availability": quantity}}
                        )
                    
                    if result.modified_count > 0:
                        inventory_updated += 1
                except Exception as e:
                    logger.error(f"Error releasing inventory for booking {booking_id}: {e}")
        
        logger.info(f"Cleaned up {expired_count} expired bookings, updated {inventory_updated} event inventories")
        
        return jsonify({
            "status": "success",
            "expired_count": expired_count,
            "inventory_updated": inventory_updated
        })
    
    except Exception as e:
        logger.error(f"Error cleaning up expired bookings: {e}")
        return jsonify({"error": str(e)}), 500

# Payment metrics endpoint for admin
@app.route('/api/admin/payment-metrics', methods=['GET'])
@log_execution_time
def get_payment_metrics():
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        if token != ADMIN_TOKEN:
            return jsonify({"error": "Invalid admin token"}), 401
        
        # Get payment metrics
        total_bookings = db.bookings.count_documents({})
        confirmed_payments = db.bookings.count_documents({"status": "confirmed"})
        pending_payments = db.bookings.count_documents({"status": "pending"})
        expired_payments = db.bookings.count_documents({"status": "expired"})
        
        # Calculate conversion rate
        conversion_rate = (confirmed_payments / total_bookings * 100) if total_bookings > 0 else 0
        
        # Calculate average time to payment
        pipeline = [
            {"$match": {"status": "confirmed", "payment_verified_at": {"$exists": True}}},
            {"$project": {
                "payment_time": {
                    "$divide": [
                        {"$subtract": ["$payment_verified_at", "$created_at"]},
                        1000 * 60  # Convert to minutes
                    ]
                }
            }},
            {"$group": {
                "_id": None,
                "avg_payment_time": {"$avg": "$payment_time"}
            }}
        ]
        
        avg_payment_result = list(db.bookings.aggregate(pipeline))
        avg_payment_time = avg_payment_result[0]["avg_payment_time"] if avg_payment_result else 0
        
        # Get recent payments
        recent_payments = list(db.bookings.find({"status": "confirmed"})
                             .sort("payment_verified_at", -1)
                             .limit(5))
        
        formatted_recent_payments = []
        for payment in recent_payments:
            # Convert MongoDB _id to string
            payment['id'] = str(payment.pop('_id')) if '_id' in payment else payment.get('booking_id')
            
            # Format dates
            if 'created_at' in payment and isinstance(payment['created_at'], datetime):
                payment['created_at'] = payment['created_at'].isoformat()
            if 'payment_verified_at' in payment and isinstance(payment['payment_verified_at'], datetime):
                payment['payment_verified_at'] = payment['payment_verified_at'].isoformat()
                
            formatted_recent_payments.append(payment)
        
        return jsonify({
            "total_bookings": total_bookings,
            "confirmed_payments": confirmed_payments,
            "pending_payments": pending_payments,
            "expired_payments": expired_payments,
            "conversion_rate": round(conversion_rate, 2),
            "avg_payment_time_minutes": round(avg_payment_time, 2) if avg_payment_time else 0,
            "recent_payments": formatted_recent_payments,
        })
    
    except Exception as e:
        logger.error(f"Error fetching payment metrics: {e}")
        return jsonify({"error": str(e)}), 500

# Ensure upload directory exists
os.makedirs("static/uploads", exist_ok=True)

@app.route('/api/events/<event_id>', methods=['PUT'])
@log_execution_time
def update_event_venue(event_id):
    # Only admin can update venue
    auth_header = request.headers.get('Authorization')
    if not check_bearer_token(auth_header):
        return 'Unauthorized', 401
    data = request.json or {}
    venue = data.get('venue')
    if not venue:
        return jsonify({'error': 'Venue is required'}), 400
    result = db.events.update_one({'_id': ObjectId(event_id)}, {'$set': {'venue': venue}})
    if result.matched_count == 0:
        return jsonify({'error': 'Event not found'}), 404
    return jsonify({'venue': venue}), 200

@app.route('/api/events/<event_id>/poster', methods=['POST'])
@log_execution_time
def upload_event_poster(event_id):
    # Only admin can update poster
    auth_header = request.headers.get('Authorization')
    if not check_bearer_token(auth_header):
        return 'Unauthorized', 401
    if 'poster' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['poster']
    filename = secure_filename(file.filename)
    file_path = os.path.join('static/uploads', filename)
    file.save(file_path)
    image_url = f'/static/uploads/{filename}'
    result = db.events.update_one({'_id': ObjectId(event_id)}, {'$set': {'image_url': image_url}})
    if result.matched_count == 0:
        return jsonify({'error': 'Event not found'}), 404
    return jsonify({'image_url': image_url}), 200

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Add public configuration endpoint for frontend
@app.route("/api/config/public", methods=["GET"])
def get_public_config():
    app.logger.info("GET /api/config/public - Retrieving public configuration")
    try:
        # Get payment settings
        payment_settings = db["payment_settings"].find_one({}, {"_id": 0})
        if not payment_settings:
            payment_settings = {
                "merchant_name": "Eventia Ticketing",
                "vpa_address": "eventia@axis",
                "payment_enabled": True,
                "default_currency": "INR",
            }
        
        # Construct the public config
        config = {
            "api_base_url": os.environ.get("API_BASE_URL", "http://localhost:3004/api"),
            "payment_enabled": payment_settings.get("payment_enabled", True),
            "merchant_name": payment_settings.get("merchant_name", "Eventia Ticketing"),
            "vpa_address": payment_settings.get("vpa_address", "eventia@axis"),
            "qr_image_url": payment_settings.get("qr_image_url", ""),
            "payment_mode": payment_settings.get("payment_mode", "vpa"),
            "default_currency": payment_settings.get("default_currency", "INR"),
        }
        
        return jsonify(config)
    except Exception as e:
        app.logger.error(f"Error retrieving public configuration: {str(e)}")
        return jsonify({"error": "Failed to retrieve configuration"}), 500

# Add endpoint to create the first admin user
@app.route('/api/admin/setup', methods=['POST'])
@log_execution_time
def admin_setup():
    try:
        # Check if admin token is provided for authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization required"}), 401
            
        token = auth_header.split(' ')[1]
        if token != ADMIN_TOKEN:
            return jsonify({"error": "Invalid admin token"}), 401
            
        # Check if any admin users already exist
        admin_count = db.admin_users.count_documents({})
        if admin_count > 0:
            return jsonify({"error": "Admin users already exist. Use admin panel to manage users."}), 400
            
        # Get admin data from request
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validate required fields
        if not username or not email or not password:
            return jsonify({"error": "Username, email and password are required"}), 400
            
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            return jsonify({"error": "Invalid email format"}), 400
            
        # Validate password length
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
            
        # Import password hashing utility
        from app.utils.password import get_password_hash
        
        # Create admin user
        from bson.objectid import ObjectId
        admin_id = ObjectId()
        
        now = datetime.now()
        admin_user = {
            "_id": admin_id,
            "username": username,
            "email": email,
            "hashed_password": get_password_hash(password),
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        
        db.admin_users.insert_one(admin_user)
        
        logger.info(f"Created first admin user: {username}")
        
        return jsonify({
            "status": "success",
            "message": "Admin user created successfully",
            "admin": {
                "id": str(admin_id),
                "username": username,
                "email": email
            }
        })
    except Exception as e:
        logger.error(f"Error in admin setup: {str(e)}", exc_info=True)
        return jsonify({"error": f"Admin setup failed: {str(e)}"}), 500

@app.route('/api/health')
def health():
    logger.info("Health check requested")
    return jsonify({ "status": "ok", "version": "1.0.0" })

if __name__ == '__main__':
    # Get port from environment or use 3004 as default
    APP_PORT = int(os.environ.get('PORT', 3004))
    
    # Get environment setting, default to production
    APP_ENV = os.environ.get('FLASK_ENV', 'production')
    
    # Configure host based on environment
    APP_HOST = '0.0.0.0'
    
    # Debug mode only in development
    DEBUG_MODE = APP_ENV == 'development'
    
    # Start memory profiler
    memory_profiler.start()
    
    logger.info(f"Starting Eventia Flask server on {APP_HOST}:{APP_PORT} in {APP_ENV} mode...")
    logger.info("API endpoints available:")
    logger.info("  GET  /api/events")
    logger.info("  GET  /api/events/<event_id>")
    logger.info("  POST /api/bookings")
    logger.info("  POST /api/verify-payment")
    logger.info("  GET  /health")
    logger.info("  GET  /metrics")
    logger.info("  GET  /api/config/public")  # Add log for new endpoint
    
    try:
        # In production, should use a proper WSGI server
        if APP_ENV == 'production':
            from waitress import serve
            serve(app, host=APP_HOST, port=APP_PORT)
        else:
            app.run(host=APP_HOST, port=APP_PORT, debug=DEBUG_MODE)
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        # Stop memory profiler when server stops
        memory_profiler.stop()