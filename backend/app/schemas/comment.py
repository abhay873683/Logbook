from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# =====================================
# Base Schema
# =====================================

class CommentBase(BaseModel):
    task_id: int
    comment: str


# =====================================
# Create Comment
# =====================================

class CommentCreate(CommentBase):
    pass


# =====================================
# Update Comment
# =====================================

class CommentUpdate(BaseModel):
    comment: Optional[str] = None


# =====================================
# Response Comment
# =====================================

class CommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    comment: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True