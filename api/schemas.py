from pydantic import BaseModel
from typing import List, Optional

class TopProduct(BaseModel):
    product: str
    count: int

class ChannelActivity(BaseModel):
    date: str
    post_count: int
    avg_views: float

class Message(BaseModel):
    message_id: int
    channel_name: str
    message_date: str
    message_text: str

class VisualStats(BaseModel):
    channel_name: str
    image_count: int
    avg_views_with_image: float