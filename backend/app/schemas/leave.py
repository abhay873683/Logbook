from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class LeaveCreate(BaseModel):
    department_id: int | None = None
    leave_type: str = Field(min_length=1, max_length=50)
    start_date: date
    end_date: date
    reason: str | None = Field(default=None, max_length=2000)


class LeaveUpdate(BaseModel):
    department_id: int | None = None
    leave_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    start_date: date | None = None
    end_date: date | None = None
    reason: str | None = Field(default=None, max_length=2000)


class LeaveRejectRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class LeaveResponse(BaseModel):
    id: int
    user_id: int
    department_id: int | None
    leave_type: str
    start_date: date
    end_date: date
    reason: str | None
    status: str
    approved_by: int | None
    approved_at: datetime | None
    rejected_by: int | None
    rejected_at: datetime | None
    rejection_reason: str | None
    comments: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaveBalanceResponse(BaseModel):
    year: int
    user_id: int
    total_allowance: int
    approved_days: int
    pending_days: int
    remaining_days: int


class LeaveSummaryResponse(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int
    cancelled: int
