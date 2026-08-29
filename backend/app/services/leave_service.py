from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.leave import Leave


VALID_LEAVE_TYPES = {
    "sick",
    "casual",
    "earned",
    "unpaid",
    "maternity",
    "paternity",
}

VALID_STATUSES = {
    "pending",
    "approved",
    "rejected",
    "cancelled",
}

ANNUAL_ALLOWANCE = 20


def normalize_leave_type(value: str):
    result = value.strip().lower()

    if result not in VALID_LEAVE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid leave type",
        )

    return result


def validate_dates(start_date, end_date):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date",
        )


def leave_days(start_date, end_date):
    return (end_date - start_date).days + 1


def check_overlap(
    db: Session,
    user_id: int,
    start_date,
    end_date,
    exclude_id=None,
):
    query = db.query(Leave).filter(
        Leave.user_id == user_id,
        Leave.status.in_(["pending", "approved"]),
        Leave.start_date <= end_date,
        Leave.end_date >= start_date,
    )

    if exclude_id is not None:
        query = query.filter(
            Leave.id != exclude_id
        )

    if query.first():
        raise HTTPException(
            status_code=409,
            detail="Overlapping leave request already exists",
        )


def create_leave(db, user_id, data):
    validate_dates(
        data.start_date,
        data.end_date,
    )

    leave_type = normalize_leave_type(
        data.leave_type
    )

    check_overlap(
        db,
        user_id,
        data.start_date,
        data.end_date,
    )

    item = Leave(
        user_id=user_id,
        department_id=data.department_id,
        leave_type=leave_type,
        start_date=data.start_date,
        end_date=data.end_date,
        reason=data.reason,
        status="pending",
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def get_leave(db, leave_id):
    item = (
        db.query(Leave)
        .filter(Leave.id == leave_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found",
        )

    return item


def update_leave(
    db,
    user_id,
    leave_id,
    data,
):
    item = get_leave(
        db,
        leave_id,
    )

    if item.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Leave access denied",
        )

    if item.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending leave can be updated",
        )

    values = data.model_dump(
        exclude_unset=True
    )

    new_start = values.get(
        "start_date",
        item.start_date,
    )

    new_end = values.get(
        "end_date",
        item.end_date,
    )

    validate_dates(
        new_start,
        new_end,
    )

    check_overlap(
        db,
        user_id,
        new_start,
        new_end,
        exclude_id=item.id,
    )

    if "leave_type" in values:
        values["leave_type"] = normalize_leave_type(
            values["leave_type"]
        )

    for key, value in values.items():
        setattr(
            item,
            key,
            value,
        )

    db.commit()
    db.refresh(item)

    return item


def delete_leave(
    db,
    user_id,
    leave_id,
):
    item = get_leave(
        db,
        leave_id,
    )

    if item.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Leave access denied",
        )

    if item.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending leave can be deleted",
        )

    db.delete(item)
    db.commit()

    return {
        "message": "Leave request deleted successfully"
    }


def approve_leave(
    db,
    leave_id,
    reviewer_id,
):
    item = get_leave(
        db,
        leave_id,
    )

    if item.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending leave can be approved",
        )

    item.status = "approved"
    item.approved_by = reviewer_id
    item.approved_at = datetime.now(
        timezone.utc
    )

    item.rejected_by = None
    item.rejected_at = None
    item.rejection_reason = None

    db.commit()
    db.refresh(item)

    return item


def reject_leave(
    db,
    leave_id,
    reviewer_id,
    reason,
):
    item = get_leave(
        db,
        leave_id,
    )

    if item.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending leave can be rejected",
        )

    item.status = "rejected"
    item.rejected_by = reviewer_id
    item.rejected_at = datetime.now(
        timezone.utc
    )
    item.rejection_reason = reason

    db.commit()
    db.refresh(item)

    return item


def get_leave_balance(
    db,
    user_id,
    year=None,
):
    year = year or date.today().year

    items = db.query(Leave).filter(
        Leave.user_id == user_id,
        Leave.start_date >= date(year, 1, 1),
        Leave.start_date <= date(year, 12, 31),
    ).all()

    approved_days = sum(
        leave_days(
            item.start_date,
            item.end_date,
        )
        for item in items
        if item.status == "approved"
        and item.leave_type != "unpaid"
    )

    pending_days = sum(
        leave_days(
            item.start_date,
            item.end_date,
        )
        for item in items
        if item.status == "pending"
        and item.leave_type != "unpaid"
    )

    remaining = max(
        ANNUAL_ALLOWANCE - approved_days,
        0,
    )

    return {
        "year": year,
        "user_id": user_id,
        "total_allowance": ANNUAL_ALLOWANCE,
        "approved_days": approved_days,
        "pending_days": pending_days,
        "remaining_days": remaining,
    }


def get_leave_summary(query):
    items = query.all()

    return {
        "total": len(items),
        "pending": sum(
            1 for x in items
            if x.status == "pending"
        ),
        "approved": sum(
            1 for x in items
            if x.status == "approved"
        ),
        "rejected": sum(
            1 for x in items
            if x.status == "rejected"
        ),
        "cancelled": sum(
            1 for x in items
            if x.status == "cancelled"
        ),
    }
