from fastapi import APIRouter, HTTPException
from app.database import db
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
async def get_analytics_summary():
    """Get total counts and waste distribution"""
    if db.db is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        # Total events
        total_events = db.db.events.count_documents({})
        
        # Waste type distribution
        pipeline = [
            {"$group": {"_id": "$class_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        distribution = list(db.db.events.aggregate(pipeline))
        
        # Format for frontend
        formatted_dist = [{"name": item["_id"] or "Unknown", "value": item["count"]} for item in distribution]
        
        return {
            "total_events": total_events,
            "distribution": formatted_dist
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timeline")
async def get_analytics_timeline(days: int = 7):
    """Get event counts over time (daily)"""
    if db.db is None:
        raise HTTPException(status_code=503, detail="Database not connected")
        
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        timeline = list(db.db.events.aggregate(pipeline))
        
        # Format dates
        formatted_timeline = []
        for item in timeline:
            date_str = f"{item['_id']['year']}-{item['_id']['month']:02d}-{item['_id']['day']:02d}"
            formatted_timeline.append({
                "date": date_str,
                "count": item["count"]
            })
            
        return formatted_timeline
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
