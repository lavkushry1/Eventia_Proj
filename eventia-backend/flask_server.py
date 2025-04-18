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
from dotenv import load_dotenv
load_dotenv()

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

@app.route('/api/events/<event_id>', methods=['PUT'])
def update_event_admin(event_id):
    """Admin-only event update (e.g., venue)"""
    auth_header = request.headers.get('Authorization')
    if not check_bearer_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        data = request.json or {}
        result = db.events.update_one({'_id': ObjectId(event_id)}, {'$set': data})
        if result.matched_count == 0:
            return jsonify({'error': 'Event not found'}), 404
        updated = db.events.find_one({'_id': ObjectId(event_id)})
        updated['id'] = str(updated.pop('_id'))
        return jsonify(updated)
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<event_id>/poster', methods=['POST'])
def upload_event_poster(event_id):
    """Admin-only upload of event poster"""
    auth_header = request.headers.get('Authorization')
    if not check_bearer_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401
    if 'poster' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['poster']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    filename = secure_filename(file.filename)
    upload_dir = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    image_url = f"/static/uploads/{filename}"
    # update DB
    db.events.update_one({'_id': ObjectId(event_id)}, {'$set': {'image_url': image_url}})
    return jsonify({'image_url': image_url})

@app.route('/api/events/<event_id>/logo', methods=['POST'])
def upload_event_logo(event_id):
    """Admin-only upload of event logo"""
    auth_header = request.headers.get('Authorization')
    if not check_bearer_token(auth_header):
        return jsonify({'error': 'Unauthorized'}), 401
    if 'logo' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['logo']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    filename = secure_filename(file.filename)
    upload_dir = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    logo_url = f"/static/uploads/{filename}"
    db.events.update_one({'_id': ObjectId(event_id)}, {'$set': {'logo_url': logo_url}})
    return jsonify({'logo_url': logo_url})

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
    port = int(os.getenv('PORT', 3002))
    host = os.getenv('HOST', '0.0.0.0')
    app.run(host=host, port=port)