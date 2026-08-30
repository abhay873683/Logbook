from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FileTypeResponse(BaseModel):
    id: int
    name: str
    extension: str
    mime_type: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FileClassificationRequest(BaseModel):
    file_name: str = Field(
        min_length=1,
        max_length=255,
    )
    mime_type: Optional[str] = Field(
        default=None,
        max_length=150,
    )


class FileClassificationResponse(BaseModel):
    file_name: str
    extension: str
    mime_type: Optional[str] = None
    category: str
    confidence: float
    reason: str
