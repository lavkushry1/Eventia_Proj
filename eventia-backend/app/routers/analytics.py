from fastapi import APIRouter, Query
from typing import Dict, Any
from ..controllers.analytics_controller import get_analytics, get_revenue_analytics, get_events_performance

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=Dict[str, Any])
async def analytics():
    """Get admin analytics dashboard data (admin only)"""
    return await get_analytics()


@router.get("/revenue", response_model=Dict[str, Any])
async def revenue_analytics(days: int = Query(30, description="Number of days to look back")):
    """Get detailed revenue analytics for a specific period (admin only)"""
    return await get_revenue_analytics(days=days)


@router.get("/events-performance", response_model=Dict[str, Any])
async def events_performance(limit: int = Query(10, description="Limit of events to return")):
    """Get performance analytics for events (admin only)"""
    return await get_events_performance(limit=limit)