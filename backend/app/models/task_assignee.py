from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TaskAssignee(Base):
    __tablename__ = "task_assignees"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    task_id = Column(
        Integer,
        ForeignKey(
            "tasks.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    assigned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    task = relationship(
        "Task",
        back_populates="task_assignees",
    )

    user = relationship(
        "User",
        back_populates="task_assignments",
    )

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "user_id",
            name="uq_task_assignee",
        ),
    )

    def __repr__(self):
        return (
            f"<TaskAssignee("
            f"task_id={self.task_id}, "
            f"user_id={self.user_id})>"
        )