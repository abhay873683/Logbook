from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TaskProgress(Base):
    __tablename__ = "task_progress"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    task_id = Column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    progress = Column(
        Integer,
        default=0
    )

    status = Column(
        String(50),
        default="In Progress"
    )

    note = Column(
        Text,
        nullable=True
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # -----------------------------
    # Relationships
    # -----------------------------

    task = relationship(
        "Task",
        back_populates="progress_history"
    )

    user = relationship(
        "User",
        back_populates="progress_updates"
    )

    def __repr__(self):
        return f"<TaskProgress {self.id}>"