from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TopProduct(BaseModel):
    product: str
    count: int

class ChannelActivity(BaseModel):
    date: str
    post_count: int
    avg_views: Optional[float] = None

class Message(BaseModel):
    message_id: int
    channel_name: str
    message_date: str
    message_text: str

class VisualStats(BaseModel):
    channel_name: str
    image_count: int
    avg_views_with_image: Optional[float] = None
    promotional_count: Optional[int] = 0

# Add these if you referenced them elsewhere
class MessageSearch(BaseModel):  # ← This was missing
    message_id: int
    channel_name: str
    message_date: str
    message_text: str
    relevance_score: Optional[float] = None