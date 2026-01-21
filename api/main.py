from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional  # ← ADD THIS LINE
import api.schemas as schemas
import api.database as database  # ← Absolute import (no dot)

app = FastAPI(
    title="Ethiopian Medical Telegram Analytics API",
    description="Analytical endpoints for medical products on Telegram",
    version="1.0.0"
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/reports/top-products", response_model=List[schemas.TopProduct])
def get_top_products(
    limit: int = Query(10, ge=1, le=50, description="Number of top products (1-50)"),
    db: Session = Depends(get_db)
):
    """Returns top mentioned terms/products across channels"""
    try:
        query = text("""
            SELECT term AS product, COUNT(*) AS count
            FROM (
                SELECT unnest(regexp_split_to_array(lower(message_text), '\\W+')) AS term
                FROM marts.fct_messages
                WHERE message_text IS NOT NULL
            ) words
            WHERE length(term) > 3
            GROUP BY term
            ORDER BY count DESC
            LIMIT :limit
        """)
        result = db.execute(query, {"limit": limit}).fetchall()
        
        if not result:
            raise HTTPException(status_code=404, detail="No products found")
            
        return [{"product": row[0], "count": row[1]} for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivity])
def get_channel_activity(
    channel_name: str, 
    db: Session = Depends(get_db)
):
    """Channel posting activity and trends"""
    try:
        query = text("""
            SELECT d.full_date::TEXT AS date, COUNT(*) AS post_count, AVG(view_count) AS avg_views
            FROM marts.fct_messages f
            JOIN marts.dim_dates d ON f.date_key = d.date_key
            JOIN marts.dim_channels c ON f.channel_key = c.channel_key
            WHERE c.channel_name = :channel_name
            GROUP BY d.full_date
            ORDER BY d.full_date DESC
            LIMIT 30
        """)
        result = db.execute(query, {"channel_name": channel_name}).fetchall()
        if not result:
            raise HTTPException(status_code=404, detail="Channel not found")
        return [{"date": row[0], "post_count": row[1], "avg_views": row[2]} for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/search/messages", response_model=List[schemas.Message])
def search_messages(
    query: str, 
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search messages containing a keyword"""
    try:
        query_str = text("""
            SELECT f.message_id, c.channel_name, f.message_date::TEXT, f.message_text
            FROM marts.fct_messages f
            JOIN marts.dim_channels c ON f.channel_key = c.channel_key
            WHERE LOWER(f.message_text) LIKE LOWER(:search_query)
            ORDER BY f.message_date DESC
            LIMIT :limit
        """)
        result = db.execute(query_str, {"search_query": f"%{query}%", "limit": limit}).fetchall()
        return [
            {
                "message_id": row[0],
                "channel_name": row[1], 
                "message_date": row[2],
                "message_text": row[3]
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/api/reports/visual-content", response_model=List[schemas.VisualStats])
def get_visual_content_stats(db: Session = Depends(get_db)):
    """Statistics about image categories across channels"""
    try:
        query = text("""
            SELECT 
                c.channel_name,
                COUNT(*) FILTER (WHERE f.has_image) AS image_count,
                AVG(f.view_count) FILTER (WHERE f.has_image) AS avg_views_with_image,
                COUNT(*) FILTER (WHERE i.image_category = 'promotional') AS promotional_count
            FROM marts.fct_messages f
            JOIN marts.dim_channels c ON f.channel_key = c.channel_key
            LEFT JOIN marts.stg_image_detections i ON f.message_id = i.message_id
            GROUP BY c.channel_name
            HAVING COUNT(*) FILTER (WHERE f.has_image) > 0
            ORDER BY image_count DESC
        """)
        result = db.execute(query).fetchall()
        return [
            {
                "channel_name": row[0],
                "image_count": row[1],
                "avg_views_with_image": round(float(row[2]), 1) if row[2] else None,
                "promotional_count": row[3] or 0
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}