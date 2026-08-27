from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(
        String(255),
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    start_time = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    end_time = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    location = Column(
        String(255),
        nullable=True,
    )

    event_type = Column(
        String(50),
        nullable=False,
        default="meeting",
        index=True,
    )

    is_all_day = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    is_recurring = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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