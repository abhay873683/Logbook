from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.sql import func

from app.core.database import Base


class EventRecurrence(Base):
    __tablename__ = "event_recurrences"

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    frequency = Column(
        String(30),
        nullable=False,
    )

    interval = Column(
        Integer,
        nullable=False,
        default=1,
    )

    days_of_week = Column(
        String(100),
        nullable=True,
    )

    day_of_month = Column(
        Integer,
        nullable=True,
    )

    recurrence_end = Column(
        DateTime(timezone=True),
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