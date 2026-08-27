from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.core.database import Base


class EventParticipant(Base):
    __tablename__ = "event_participants"

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "user_id",
            name="uq_event_participant",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(
        String(30),
        nullable=False,
        default="participant",
    )

    status = Column(
        String(30),
        nullable=False,
        default="accepted",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )