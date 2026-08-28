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
    notes: Optional[str] = None


class TimesheetUpdate(BaseModel):
    notes: Optional[str] = None


class TimesheetResponse(BaseModel):
    id: int
    user_id: int
    date: date
    total_seconds: int
    status: str

    submitted_at: Optional[datetime] = None

    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None

    rejected_at: Optional[datetime] = None
    rejected_by: Optional[int] = None
    rejection_reason: Optional[str] = None

    notes: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimesheetRejectRequest(BaseModel):
    reason: str = Field(
        min_length=1,
        max_length=1000,
    )


class TimesheetLogCreate(BaseModel):
    date: date
    task_id: Optional[int] = None
    description: Optional[str] = None

    hours: float = Field(
        gt=0,
        le=24,
    )

    is_billable: bool = True


class TimesheetLogResponse(BaseModel):
    id: int
    timesheet_id: int
    date: date
    task_id: Optional[int] = None
    description: Optional[str] = None
    hours: float
    is_billable: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimeSummaryResponse(BaseModel):
    total_seconds: int = Field(default=0, ge=0)
    billable_seconds: int = Field(default=0, ge=0)
    non_billable_seconds: int = Field(default=0, ge=0)
    total_entries: int = Field(default=0, ge=0)


class TimesheetSummaryResponse(BaseModel):
    total_timesheets: int = 0
    draft: int = 0
    submitted: int = 0
    approved: int = 0
    rejected: int = 0
    total_seconds: int = 0
    total_hours: float = 0.0
