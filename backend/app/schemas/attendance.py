from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class AttendanceCreate(BaseModel):
    department_id: int | None = None
    date: date
    check_in: datetime | None = None
    check_out: datetime | None = None
    status: str = Field(default="present", max_length=30)
    notes: str | None = Field(default=None, max_length=2000)


class AttendanceUpdate(BaseModel):
    department_id: int | None = None
    check_in: datetime | None = None
    check_out: datetime | None = None
    status: str | None = Field(default=None, max_length=30)
    notes: str | None = Field(default=None, max_length=2000)


class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    department_id: int | None
    date: date
    check_in: datetime | None
    check_out: datetime | None
    status: str
    hours_worked: float
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttendanceSummaryResponse(BaseModel):
    total_days: int
    present: int
    absent: int
    half_day: int
    leave: int
    total_hours: float
