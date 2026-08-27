from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TimeLogCreate(BaseModel):
    task_id: int
    project_id: int
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_billable: bool = True


class TimeLogUpdate(BaseModel):
    task_id: Optional[int] = None
    project_id: Optional[int] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_billable: Optional[bool] = None


class TimeLogResponse(BaseModel):
    id: int
    user_id: int
    task_id: int
    project_id: int
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    duration: int
    is_billable: bool
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimerStartRequest(BaseModel):
    task_id: int
    project_id: int
    description: Optional[str] = None
    is_billable: bool = True


class TimerSessionResponse(BaseModel):
    id: int
    user_id: int
    task_id: int
    project_id: int
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool
    is_billable: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimerStopResponse(BaseModel):
    timer_session: TimerSessionResponse
    time_log: TimeLogResponse


class TimesheetCreate(BaseModel):
    date: date


class TimesheetResponse(BaseModel):
    id: int
    user_id: int
    date: date
    total_seconds: int
    status: str
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimeSummaryResponse(BaseModel):
    total_seconds: int = Field(default=0, ge=0)
    billable_seconds: int = Field(default=0, ge=0)
    non_billable_seconds: int = Field(default=0, ge=0)
    total_entries: int = Field(default=0, ge=0)