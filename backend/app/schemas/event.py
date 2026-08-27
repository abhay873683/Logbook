from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    event_type: str = "meeting"
    is_all_day: bool = False


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    is_all_day: Optional[bool] = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    event_type: str
    is_all_day: bool
    is_recurring: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParticipantCreate(BaseModel):
    user_id: int
    role: str = "participant"


class ParticipantResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    role: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecurrenceCreate(BaseModel):
    frequency: str
    interval: int = Field(default=1, ge=1)
    days_of_week: Optional[str] = None
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    recurrence_end: Optional[datetime] = None


class RecurrenceResponse(BaseModel):
    id: int
    event_id: int
    frequency: str
    interval: int
    days_of_week: Optional[str] = None
    day_of_month: Optional[int] = None
    recurrence_end: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)