from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import text
from typing import List
from contextlib import asynccontextmanager
import api.schemas as schemas
from api.database import get_db

app = FastAPI(
    title="Ethiopian Medical Telegram Analytics API",
    description="Analytical endpoints for medical products on Telegram",
    version="1.0.0"
)

# Optional: startup event (e.g. check connection)
@app.on_event("startup")
async def startup():
    pass  # can add health checks here

@app.get("/api/reports/top-products", response_model=List[schemas.TopProduct])
def get_top_products(
    limit: int = Query(10, ge=1, le=50, description="Number of top products (1-50)"),
    db=Depends(get_db)
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


@app.get("/api/reports/visual-content", response_model=List[schemas.VisualStats])
def get_visual_content_stats(db=Depends(get_db)):
    """Statistics about image categories across channels"""
    try:
        query = text("""
            SELECT 
                c.channel_name,
                COUNT(*) FILTER (WHERE has_image) AS total_images,
                COUNT(*) FILTER (WHERE image_category = 'promotional') AS promotional_count,
                COUNT(*) FILTER (WHERE image_category = 'product_display') AS product_display_count,
                AVG(view_count) FILTER (WHERE has_image) AS avg_views_with_image
            FROM marts.fct_message_with_images f
            JOIN marts.dim_channels c ON f.channel_key = c.channel_key
            GROUP BY c.channel_name
            HAVING COUNT(*) FILTER (WHERE has_image) > 0
            ORDER BY total_images DESC
        """)
        result = db.execute(query).fetchall()
        return [
            {
                "channel_name": r[0],
                "total_images": r[1],
                "promotional_count": r[2],
                "product_display_count": r[3],
                "avg_views_with_image": round(float(r[4]), 1) if r[4] else None
            }
            for r in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# Add the other endpoints similarly (channel activity, message search)
# with proper error handling, query parameter validation and clean SQL