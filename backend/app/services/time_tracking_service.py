from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.time_log import TimeLog
from app.models.timer_session import TimerSession
from app.models.timesheet import Timesheet
from app.schemas.time_tracking import (
    TimeLogCreate,
    TimeLogUpdate,
    TimerStartRequest,
)
from app.utils.time_utils import calculate_duration_seconds, utc_now


def create_time_log(
    db: Session,
    user_id: int,
    data: TimeLogCreate,
):
    try:
        duration = calculate_duration_seconds(
            data.start_time,
            data.end_time,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    time_log = TimeLog(
        user_id=user_id,
        task_id=data.task_id,
        project_id=data.project_id,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        duration=duration,
        is_billable=data.is_billable,
        source="manual",
    )

    db.add(time_log)
    db.commit()
    db.refresh(time_log)

    return time_log


def get_time_logs(
    db: Session,
    user_id: int,
):
    return (
        db.query(TimeLog)
        .filter(TimeLog.user_id == user_id)
        .order_by(TimeLog.created_at.desc())
        .all()
    )


def get_time_log(
    db: Session,
    user_id: int,
    time_log_id: int,
):
    time_log = (
        db.query(TimeLog)
        .filter(
            TimeLog.id == time_log_id,
            TimeLog.user_id == user_id,
        )
        .first()
    )

    if not time_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time log not found",
        )

    return time_log


def update_time_log(
    db: Session,
    user_id: int,
    time_log_id: int,
    data: TimeLogUpdate,
):
    time_log = get_time_log(
        db,
        user_id,
        time_log_id,
    )

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(time_log, field, value)

    try:
        time_log.duration = calculate_duration_seconds(
            time_log.start_time,
            time_log.end_time,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    db.commit()
    db.refresh(time_log)

    return time_log


def delete_time_log(
    db: Session,
    user_id: int,
    time_log_id: int,
):
    time_log = get_time_log(
        db,
        user_id,
        time_log_id,
    )

    db.delete(time_log)
    db.commit()

    return {"message": "Time log deleted successfully"}


def start_timer(
    db: Session,
    user_id: int,
    data: TimerStartRequest,
):
    existing_timer = (
        db.query(TimerSession)
        .filter(
            TimerSession.user_id == user_id,
            TimerSession.is_active.is_(True),
        )
        .first()
    )

    if existing_timer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active timer already exists",
        )

    timer = TimerSession(
        user_id=user_id,
        task_id=data.task_id,
        project_id=data.project_id,
        description=data.description,
        is_billable=data.is_billable,
        start_time=utc_now(),
        is_active=True,
    )

    db.add(timer)
    db.commit()
    db.refresh(timer)

    return timer


def get_active_timer(
    db: Session,
    user_id: int,
):
    return (
        db.query(TimerSession)
        .filter(
            TimerSession.user_id == user_id,
            TimerSession.is_active.is_(True),
        )
        .first()
    )


def get_timer_history(
    db: Session,
    user_id: int,
):
    return (
        db.query(TimerSession)
        .filter(TimerSession.user_id == user_id)
        .order_by(TimerSession.created_at.desc())
        .all()
    )


def stop_timer(
    db: Session,
    user_id: int,
):
    timer = get_active_timer(db, user_id)

    if not timer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active timer found",
        )

    timer.end_time = utc_now()
    timer.is_active = False

    duration = calculate_duration_seconds(
        timer.start_time,
        timer.end_time,
    )

    time_log = TimeLog(
        user_id=user_id,
        task_id=timer.task_id,
        project_id=timer.project_id,
        description=timer.description,
        start_time=timer.start_time,
        end_time=timer.end_time,
        duration=duration,
        is_billable=timer.is_billable,
        source="timer",
    )

    db.add(time_log)
    db.commit()

    db.refresh(timer)
    db.refresh(time_log)

    return {
        "timer_session": timer,
        "time_log": time_log,
    }


def get_time_summary(
    db: Session,
    user_id: int,
):
    logs = (
        db.query(TimeLog)
        .filter(TimeLog.user_id == user_id)
        .all()
    )

    total_seconds = sum(log.duration or 0 for log in logs)

    billable_seconds = sum(
        log.duration or 0
        for log in logs
        if log.is_billable
    )

    non_billable_seconds = total_seconds - billable_seconds

    return {
        "total_seconds": total_seconds,
        "billable_seconds": billable_seconds,
        "non_billable_seconds": non_billable_seconds,
        "total_entries": len(logs),
    }


def get_timesheets(
    db: Session,
    user_id: int,
):
    return (
        db.query(Timesheet)
        .filter(Timesheet.user_id == user_id)
        .order_by(Timesheet.date.desc())
        .all()
    )


def create_or_refresh_timesheet(
    db: Session,
    user_id: int,
    target_date: date,
):
    logs = (
        db.query(TimeLog)
        .filter(
            TimeLog.user_id == user_id,
        )
        .all()
    )

    total_seconds = sum(
        log.duration or 0
        for log in logs
        if log.start_time.date() == target_date
    )

    timesheet = (
        db.query(Timesheet)
        .filter(
            Timesheet.user_id == user_id,
            Timesheet.date == target_date,
        )
        .first()
    )

    if not timesheet:
        timesheet = Timesheet(
            user_id=user_id,
            date=target_date,
            total_seconds=total_seconds,
            status="draft",
        )
        db.add(timesheet)
    else:
        if timesheet.status == "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approved timesheet cannot be refreshed",
            )

        timesheet.total_seconds = total_seconds

    db.commit()
    db.refresh(timesheet)

    return timesheet


def submit_timesheet(
    db: Session,
    user_id: int,
    timesheet_id: int,
):
    timesheet = (
        db.query(Timesheet)
        .filter(
            Timesheet.id == timesheet_id,
            Timesheet.user_id == user_id,
        )
        .first()
    )

    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found",
        )

    if timesheet.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timesheet is already approved",
        )

    timesheet.status = "submitted"
    timesheet.submitted_at = utc_now()

    db.commit()
    db.refresh(timesheet)

    return timesheet


def approve_timesheet(
    db: Session,
    timesheet_id: int,
    approved_by: int,
):
    timesheet = (
        db.query(Timesheet)
        .filter(Timesheet.id == timesheet_id)
        .first()
    )

    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found",
        )

    if timesheet.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only submitted timesheets can be approved",
        )

    timesheet.status = "approved"
    timesheet.approved_at = utc_now()
    timesheet.approved_by = approved_by

    db.commit()
    db.refresh(timesheet)

    return timesheet