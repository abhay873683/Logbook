from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.core.database import Base


class Attendance(Base):
    __tablename__ = "attendance_logs"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "date",
            name="uq_attendance_user_date",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    department_id = Column(
        Integer,
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    date = Column(
        Date,
        nullable=False,
        index=True,
    )

    check_in = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    check_out = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="present",
        index=True,
    )

    hours_worked = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
