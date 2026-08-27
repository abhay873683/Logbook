from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user

from app.schemas.time_tracking import (
    TimeLogCreate,
    TimeLogResponse,
    TimeLogUpdate,
    TimeSummaryResponse,
    TimerSessionResponse,
    TimerStartRequest,
    TimerStopResponse,
    TimesheetCreate,
    TimesheetResponse,
)

from app.services.time_tracking_service import (
    approve_timesheet,
    create_or_refresh_timesheet,
    create_time_log,
    delete_time_log,
    get_active_timer,
    get_time_log,
    get_time_logs,
    get_time_summary,
    get_timer_history,
    get_timesheets,
    start_timer,
    stop_timer,
    submit_timesheet,
    update_time_log,
)


router = APIRouter()


@router.post(
    "/logs/",
    response_model=TimeLogResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_time_log(
    data: TimeLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_time_log(
        db,
        current_user.id,
        data,
    )


@router.get(
    "/logs/",
    response_model=list[TimeLogResponse],
)
def read_time_logs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_time_logs(
        db,
        current_user.id,
    )


@router.get(
    "/logs/{time_log_id}",
    response_model=TimeLogResponse,
)
def read_time_log(
    time_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_time_log(
        db,
        current_user.id,
        time_log_id,
    )


@router.put(
    "/logs/{time_log_id}",
    response_model=TimeLogResponse,
)
def edit_time_log(
    time_log_id: int,
    data: TimeLogUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return update_time_log(
        db,
        current_user.id,
        time_log_id,
        data,
    )


@router.delete("/logs/{time_log_id}")
def remove_time_log(
    time_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return delete_time_log(
        db,
        current_user.id,
        time_log_id,
    )


@router.post(
    "/timer/start",
    response_model=TimerSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_user_timer(
    data: TimerStartRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return start_timer(
        db,
        current_user.id,
        data,
    )


@router.post(
    "/timer/stop",
    response_model=TimerStopResponse,
)
def stop_user_timer(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return stop_timer(
        db,
        current_user.id,
    )


@router.get(
    "/timer/active",
    response_model=TimerSessionResponse | None,
)
def read_active_timer(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_active_timer(
        db,
        current_user.id,
    )


@router.get(
    "/timer/history",
    response_model=list[TimerSessionResponse],
)
def read_timer_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_timer_history(
        db,
        current_user.id,
    )


@router.get(
    "/summary",
    response_model=TimeSummaryResponse,
)
def read_time_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_time_summary(
        db,
        current_user.id,
    )


@router.get(
    "/timesheets/",
    response_model=list[TimesheetResponse],
)
def read_timesheets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_timesheets(
        db,
        current_user.id,
    )


@router.post(
    "/timesheets/",
    response_model=TimesheetResponse,
)
def create_timesheet(
    data: TimesheetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_or_refresh_timesheet(
        db,
        current_user.id,
        data.date,
    )


@router.post(
    "/timesheets/{timesheet_id}/submit",
    response_model=TimesheetResponse,
)
def submit_user_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return submit_timesheet(
        db,
        current_user.id,
        timesheet_id,
    )


@router.post(
    "/timesheets/{timesheet_id}/approve",
    response_model=TimesheetResponse,
)
def approve_user_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return approve_timesheet(
        db,
        timesheet_id,
        current_user.id,
    )