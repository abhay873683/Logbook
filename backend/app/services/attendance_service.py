from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.attendance import Attendance


VALID_ATTENDANCE_STATUSES = {
    "present",
    "absent",
    "half_day",
    "leave",
}


def normalize_status(value):
    status = value.strip().lower()

    if status not in VALID_ATTENDANCE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid attendance status",
        )

    return status


def calculate_hours(
    check_in,
    check_out,
):
    if not check_in or not check_out:
        return 0.0

    if check_out <= check_in:
        raise HTTPException(
            status_code=400,
            detail="check_out must be after check_in",
        )

    seconds = (
        check_out - check_in
    ).total_seconds()

    return round(
        seconds / 3600,
        2,
    )


def create_attendance(
    db: Session,
    user_id: int,
    data,
):
    existing = db.query(
        Attendance
    ).filter(
        Attendance.user_id == user_id,
        Attendance.date == data.date,
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Attendance already logged for this date",
        )

    status = normalize_status(
        data.status
    )

    hours = calculate_hours(
        data.check_in,
        data.check_out,
    )

    item = Attendance(
        user_id=user_id,
        department_id=data.department_id,
        date=data.date,
        check_in=data.check_in,
        check_out=data.check_out,
        status=status,
        hours_worked=hours,
        notes=data.notes,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def get_attendance(
    db,
    attendance_id,
):
    item = db.query(
        Attendance
    ).filter(
        Attendance.id == attendance_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Attendance record not found",
        )

    return item


def update_attendance(
    db,
    attendance_id,
    data,
):
    item = get_attendance(
        db,
        attendance_id,
    )

    values = data.model_dump(
        exclude_unset=True
    )

    if "status" in values:
        values["status"] = normalize_status(
            values["status"]
        )

    for key, value in values.items():
        setattr(
            item,
            key,
            value,
        )

    item.hours_worked = calculate_hours(
        item.check_in,
        item.check_out,
    )

    db.commit()
    db.refresh(item)

    return item


def attendance_summary(query):
    items = query.all()

    return {
        "total_days": len(items),
        "present": sum(
            1 for x in items
            if x.status == "present"
        ),
        "absent": sum(
            1 for x in items
            if x.status == "absent"
        ),
        "half_day": sum(
            1 for x in items
            if x.status == "half_day"
        ),
        "leave": sum(
            1 for x in items
            if x.status == "leave"
        ),
        "total_hours": round(
            sum(
                float(x.hours_worked or 0)
                for x in items
            ),
            2,
        ),
    }
