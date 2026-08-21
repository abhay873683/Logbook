from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommentReplyCreate(BaseModel):
    comment_id: int
    reply: str

class CommentReplyResponse(BaseModel):
    id: int
    comment_id: int
    user_id: int
    reply: str
    created_at: datetime

    class Config:
        from_attributes = True