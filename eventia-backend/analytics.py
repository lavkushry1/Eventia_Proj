from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import our database connection
from database import get_db, serialize_object_id

# Import auth utilities
from auth import verify_admin_token

# Create router
router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=Dict[str, Any])
async def get_analytics(
    db: MongoClient = Depends(get_db),
    _: bool = Depends(verify_admin_token)
):
    """Get admin analytics dashboard data (admin only)"""
    # Get total bookings
    total_bookings = db.bookings.count_documents({})
    
    # Get bookings with various statuses
    pending_bookings = db.bookings.count_documents({"status": "pending"})
    confirmed_bookings = db.bookings.count_documents({"status": "confirmed"})
    dispatched_bookings = db.bookings.count_documents({"status": "dispatched"})
    
    # Get payment statuses
    pending_payments = db.bookings.count_documents({"payment_status": "pending"})
    pending_verification = db.bookings.count_documents({"payment_status": "pending_verification"})
    completed_payments = db.bookings.count_documents({"payment_status": "completed"})
    
    # Calculate total revenue
    revenue_pipeline = [
        {"$match": {"payment_status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]
    revenue_result = list(db.bookings.aggregate(revenue_pipeline))
    total_revenue = revenue_result[0]["total"] if revenue_result else 0
    
    # Get revenue by date (last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    revenue_by_date_pipeline = [
        {"$match": {"payment_status": "completed"}},
        {"$group": {
            "_id": {"$substr": ["$booking_date", 0, 10]},
            "daily_revenue": {"$sum": "$total_amount"}
        }},
        {"$sort": {"_id": 1}}
    ]
    revenue_by_date = list(db.bookings.aggregate(revenue_by_date_pipeline))
    
    # Get event popularity
    event_popularity_pipeline = [
        {"$group": {
            "_id": "$event_id",
            "ticket_count": {"$sum": "$quantity"}
        }},
        {"$sort": {"ticket_count": -1}},
        {"$limit": 10}
    ]
    popular_events_raw = list(db.bookings.aggregate(event_popularity_pipeline))
    
    # Get event details for popular events
    popular_events = []
    for event in popular_events_raw:
        try:
            event_details = db.events.find_one({"_id": ObjectId(event["_id"])})
            if event_details:
                popular_events.append({
                    "event_id": str(event["_id"]),
                    "event_name": event_details["name"],
                    "ticket_count": event["ticket_count"]
                })
        except:
            # Skip if event ID is invalid or event not found
            continue
    
    # Get user activity data (unique users by day)
    user_activity_pipeline = [
        {"$group": {
            "_id": {"$substr": ["$booking_date", 0, 10]},
            "unique_users": {"$addToSet": "$address.email"}
        }},
        {"$project": {
            "date": "$_id",
            "count": {"$size": "$unique_users"}
        }},
        {"$sort": {"date": 1}}
    ]
    user_activity = list(db.bookings.aggregate(user_activity_pipeline))
    
    return {
        "summary": {
            "total_bookings": total_bookings,
            "total_revenue": total_revenue,
            "pending_bookings": pending_bookings,
            "confirmed_bookings": confirmed_bookings,
            "dispatched_bookings": dispatched_bookings
        },
        "payment_status": {
            "pending": pending_payments,
            "pending_verification": pending_verification,
            "completed": completed_payments
        },
        "revenue_trends": serialize_object_id(revenue_by_date),
        "popular_events": popular_events,
        "user_activity": serialize_object_id(user_activity)
    }

@router.get("/revenue", response_model=Dict[str, Any])
async def get_revenue_analytics(
    days: int = 30,
    db: MongoClient = Depends(get_db),
    _: bool = Depends(verify_admin_token)
):
    """Get detailed revenue analytics for a specific period (admin only)"""
    # Calculate the date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates for query
    start_date_str = start_date.strftime("%Y-%m-%d")
    
    # Pipeline for daily revenue
    daily_revenue_pipeline = [
        {"$match": {
            "payment_status": "completed",
            "booking_date": {"$gte": start_date_str}
        }},
        {"$group": {
            "_id": {"$substr": ["$booking_date", 0, 10]},
            "daily_revenue": {"$sum": "$total_amount"},
            "ticket_count": {"$sum": "$quantity"}
        }},
        {"$sort": {"_id": 1}}
    ]
    daily_revenue = list(db.bookings.aggregate(daily_revenue_pipeline))
    
    # Pipeline for revenue by category
    category_revenue_pipeline = [
        {"$match": {
            "payment_status": "completed",
            "booking_date": {"$gte": start_date_str}
        }},
        {"$lookup": {
            "from": "events",
            "localField": "event_id",
            "foreignField": "_id",
            "as": "event_details"
        }},
        {"$unwind": "$event_details"},
        {"$group": {
            "_id": "$event_details.category",
            "total_revenue": {"$sum": "$total_amount"},
            "ticket_count": {"$sum": "$quantity"}
        }},
        {"$sort": {"total_revenue": -1}}
    ]
    
    # Try to run the category pipeline, but handle potential issues with ObjectId conversion
    try:
        category_revenue = list(db.bookings.aggregate(category_revenue_pipeline))
    except:
        # Fallback to a simpler query if the lookup fails
        category_revenue = []
    
    return {
        "daily_revenue": serialize_object_id(daily_revenue),
        "category_revenue": serialize_object_id(category_revenue),
        "period_days": days
    }

@router.get("/events-performance", response_model=Dict[str, Any])
async def get_events_performance(
    limit: int = 10,
    db: MongoClient = Depends(get_db),
    _: bool = Depends(verify_admin_token)
):
    """Get performance analytics for events (admin only)"""
    # Get top selling events
    top_events_pipeline = [
        {"$group": {
            "_id": "$event_id",
            "ticket_count": {"$sum": "$quantity"},
            "revenue": {"$sum": "$total_amount"}
        }},
        {"$sort": {"ticket_count": -1}},
        {"$limit": limit}
    ]
    top_events_raw = list(db.bookings.aggregate(top_events_pipeline))
    
    # Get event details for each top event
    top_events = []
    for event in top_events_raw:
        try:
            event_details = db.events.find_one({"_id": ObjectId(event["_id"])})
            if event_details:
                top_events.append({
                    "event_id": str(event["_id"]),
                    "event_name": event_details["name"],
                    "ticket_count": event["ticket_count"],
                    "revenue": event["revenue"],
                    "category": event_details.get("category", "Unknown"),
                    "venue": event_details.get("venue", "Unknown"),
                    "date": event_details.get("date", "Unknown")
                })
        except:
            # Skip if event ID is invalid or event not found
            continue
    
    # Calculate sell-through rate for each event
    events_with_availability = list(db.events.find({}, {"name": 1, "availability": 1}))
    sell_through_rates = []
    
    for event in events_with_availability:
        # Get original capacity (current availability + tickets sold)
        original_capacity = event.get("availability", 0)
        
        # Get tickets sold
        tickets_sold_pipeline = [
            {"$match": {"event_id": str(event["_id"])}},
            {"$group": {"_id": None, "total_sold": {"$sum": "$quantity"}}}
        ]
        tickets_sold_result = list(db.bookings.aggregate(tickets_sold_pipeline))
        tickets_sold = tickets_sold_result[0]["total_sold"] if tickets_sold_result else 0
        
        # Calculate total capacity and sell-through rate
        total_capacity = original_capacity + tickets_sold
        sell_through_rate = (tickets_sold / total_capacity * 100) if total_capacity > 0 else 0
        
        sell_through_rates.append({
            "event_id": str(event["_id"]),
            "event_name": event.get("name", "Unknown"),
            "total_capacity": total_capacity,
            "tickets_sold": tickets_sold,
            "sell_through_rate": round(sell_through_rate, 2)
        })
    
    # Sort by sell-through rate
    sell_through_rates.sort(key=lambda x: x["sell_through_rate"], reverse=True)
    
    return {
        "top_selling_events": top_events,
        "sell_through_rates": sell_through_rates[:limit]
    } 