from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.core.database import Base


class Timesheet(Base):
    __tablename__ = "timesheets"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "date",
            name="uq_timesheet_user_date",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date = Column(
        Date,
        nullable=False,
        index=True,
    )

    # Total tracked time for this day in seconds
    total_seconds = Column(
        Integer,
        nullable=False,
        default=0,
    )

    # draft -> submitted -> approved
    status = Column(
        String(30),
        nullable=False,
        default="draft",
        index=True,
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    approved_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    approved_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
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