"""
Utility functions for discount analytics and reporting.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

from app.core.database import db
from app.models.discount import get_discount_by_id

logger = logging.getLogger(__name__)

async def get_discount_usage_stats(discount_id: str = None, days: int = 30) -> Dict[str, Any]:
    """
    Get usage statistics for a specific discount code or all discounts.
    
    Args:
        discount_id: Optional ID of a specific discount to analyze
        days: Number of days to analyze (default 30)
        
    Returns:
        Dictionary with usage statistics
    """
    try:
        # Define the date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        start_date_str = start_date.isoformat()
        
        # Build the query
        match_stage = {
            "booking_date": {"$gte": start_date_str},
            "status": {"$in": ["confirmed", "pending"]}
        }
        
        if discount_id:
            # Get the discount code
            discount = await get_discount_by_id(discount_id)
            if not discount:
                return {
                    "error": f"Discount with ID {discount_id} not found"
                }
            
            match_stage["discount_code"] = discount.get("code")
        else:
            # Only include bookings with discount codes
            match_stage["discount_code"] = {"$exists": True, "$ne": None}
        
        # Aggregate bookings with discounts
        pipeline = [
            {"$match": match_stage},
            {"$group": {
                "_id": "$discount_code",
                "usage_count": {"$sum": 1},
                "total_discount_amount": {"$sum": "$discount_amount"},
                "total_booking_value": {"$sum": "$total_amount"},
                "avg_discount_amount": {"$avg": "$discount_amount"},
                "bookings": {"$push": {
                    "booking_id": "$booking_id", 
                    "date": "$booking_date",
                    "discount_amount": "$discount_amount",
                    "customer_email": "$customer_info.email"
                }}
            }},
            {"$sort": {"usage_count": -1}}
        ]
        
        results = await db.bookings.aggregate(pipeline).to_list(length=100)
        
        # Format the results
        if discount_id:
            # Return detailed stats for single discount
            if not results:
                return {
                    "discount_id": discount_id,
                    "discount_code": discount.get("code") if discount else None,
                    "usage_count": 0,
                    "total_discount_amount": 0,
                    "total_booking_value": 0,
                    "conversion_rate": 0,
                    "bookings": []
                }
            
            result = results[0]
            return {
                "discount_id": discount_id,
                "discount_code": result["_id"],
                "usage_count": result["usage_count"],
                "total_discount_amount": result["total_discount_amount"],
                "total_booking_value": result["total_booking_value"],
                "avg_discount_amount": result["avg_discount_amount"],
                "discount_percentage": (result["total_discount_amount"] / (result["total_booking_value"] + result["total_discount_amount"])) * 100 if result["total_booking_value"] > 0 else 0,
                "bookings": result["bookings"]
            }
        else:
            # Return summary stats for all discounts
            total_usage = sum(r["usage_count"] for r in results)
            total_discount_amount = sum(r["total_discount_amount"] for r in results)
            total_booking_value = sum(r["total_booking_value"] for r in results)
            
            return {
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "total_discount_usage": total_usage,
                "total_discount_amount": total_discount_amount,
                "total_booking_value": total_booking_value,
                "discount_percentage": (total_discount_amount / (total_booking_value + total_discount_amount)) * 100 if total_booking_value > 0 else 0,
                "discounts": [
                    {
                        "discount_code": r["_id"],
                        "usage_count": r["usage_count"],
                        "total_discount_amount": r["total_discount_amount"],
                        "usage_percentage": (r["usage_count"] / total_usage) * 100 if total_usage > 0 else 0
                    } for r in results
                ]
            }
    
    except Exception as e:
        logger.error(f"Error getting discount usage stats: {str(e)}")
        return {"error": f"Error analyzing discount usage: {str(e)}"}


async def get_discount_effectiveness_report() -> Dict[str, Any]:
    """
    Generate a report on discount effectiveness, comparing conversion rates
    of bookings with and without discounts.
    
    Returns:
        Dictionary with effectiveness metrics
    """
    try:
        # Define the date range (last 90 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        start_date_str = start_date.isoformat()
        
        # Total bookings
        total_bookings = await db.bookings.count_documents({
            "booking_date": {"$gte": start_date_str}
        })
        
        # Bookings with discounts
        discount_bookings = await db.bookings.count_documents({
            "booking_date": {"$gte": start_date_str},
            "discount_code": {"$exists": True, "$ne": None}
        })
        
        # Confirmed bookings with discounts
        confirmed_discount_bookings = await db.bookings.count_documents({
            "booking_date": {"$gte": start_date_str},
            "discount_code": {"$exists": True, "$ne": None},
            "status": "confirmed"
        })
        
        # Confirmed bookings without discounts
        confirmed_regular_bookings = await db.bookings.count_documents({
            "booking_date": {"$gte": start_date_str},
            "$or": [
                {"discount_code": {"$exists": False}},
                {"discount_code": None}
            ],
            "status": "confirmed"
        })
        
        # Regular bookings (no discount)
        regular_bookings = total_bookings - discount_bookings
        
        # Calculate conversion rates
        discount_conversion_rate = (confirmed_discount_bookings / discount_bookings) * 100 if discount_bookings > 0 else 0
        regular_conversion_rate = (confirmed_regular_bookings / regular_bookings) * 100 if regular_bookings > 0 else 0
        
        # Revenue analysis
        discount_revenue_pipeline = [
            {"$match": {
                "booking_date": {"$gte": start_date_str},
                "discount_code": {"$exists": True, "$ne": None},
                "status": "confirmed"
            }},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$total_amount"},
                "total_discount": {"$sum": "$discount_amount"},
                "average_order_value": {"$avg": "$total_amount"}
            }}
        ]
        
        regular_revenue_pipeline = [
            {"$match": {
                "booking_date": {"$gte": start_date_str},
                "$or": [
                    {"discount_code": {"$exists": False}},
                    {"discount_code": None}
                ],
                "status": "confirmed"
            }},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$total_amount"},
                "average_order_value": {"$avg": "$total_amount"}
            }}
        ]
        
        discount_revenue_results = await db.bookings.aggregate(discount_revenue_pipeline).to_list(length=1)
        regular_revenue_results = await db.bookings.aggregate(regular_revenue_pipeline).to_list(length=1)
        
        discount_revenue_data = discount_revenue_results[0] if discount_revenue_results else {"total_revenue": 0, "total_discount": 0, "average_order_value": 0}
        regular_revenue_data = regular_revenue_results[0] if regular_revenue_results else {"total_revenue": 0, "average_order_value": 0}
        
        return {
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "total_bookings": total_bookings,
            "discount_usage": {
                "bookings_with_discount": discount_bookings,
                "percentage_with_discount": (discount_bookings / total_bookings) * 100 if total_bookings > 0 else 0
            },
            "conversion_rates": {
                "with_discount": discount_conversion_rate,
                "without_discount": regular_conversion_rate,
                "difference": discount_conversion_rate - regular_conversion_rate
            },
            "revenue_impact": {
                "with_discount": {
                    "total_revenue": discount_revenue_data.get("total_revenue", 0),
                    "total_discount_amount": discount_revenue_data.get("total_discount", 0),
                    "average_order_value": discount_revenue_data.get("average_order_value", 0)
                },
                "without_discount": {
                    "total_revenue": regular_revenue_data.get("total_revenue", 0),
                    "average_order_value": regular_revenue_data.get("average_order_value", 0)
                },
                "aov_difference": discount_revenue_data.get("average_order_value", 0) - regular_revenue_data.get("average_order_value", 0)
            },
            "recommendation": get_discount_recommendation(
                discount_conversion_rate, 
                regular_conversion_rate,
                discount_revenue_data.get("average_order_value", 0),
                regular_revenue_data.get("average_order_value", 0),
                discount_revenue_data.get("total_discount", 0)
            )
        }
    
    except Exception as e:
        logger.error(f"Error generating discount effectiveness report: {str(e)}")
        return {"error": f"Error generating report: {str(e)}"}


def get_discount_recommendation(
    discount_conversion: float,
    regular_conversion: float,
    discount_aov: float,
    regular_aov: float,
    total_discount_amount: float
) -> str:
    """
    Generate a recommendation based on discount effectiveness metrics.
    """
    if discount_conversion - regular_conversion > 10:
        if discount_aov >= regular_aov:
            return "Discounts are highly effective at increasing conversion and maintaining/increasing order value. Consider expanding discount programs."
        else:
            conversion_lift = discount_conversion - regular_conversion
            aov_reduction = regular_aov - discount_aov
            if (conversion_lift * discount_aov) > (aov_reduction * regular_conversion):
                return "Discounts are increasing overall revenue despite lower order values. Continue with current discount strategy."
            else:
                return "While discounts improve conversion, they significantly reduce order value. Consider adjusting discount amounts or targeting."
    elif discount_conversion - regular_conversion > 0:
        return "Discounts show minor improvement in conversion rates. Experiment with different discount types or targeting strategies."
    else:
        return "Current discounts don't appear to boost conversion rates. Consider revising your discount strategy or focusing on other marketing approaches."
