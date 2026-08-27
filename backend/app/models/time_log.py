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


class TimeLog(Base):
    __tablename__ = "time_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    task_id = Column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    description = Column(Text, nullable=True)

    start_time = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    end_time = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Duration is stored in seconds.
    duration = Column(
        Integer,
        nullable=False,
        default=0,
    )

    is_billable = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    source = Column(
        String(30),
        nullable=False,
        default="manual",
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