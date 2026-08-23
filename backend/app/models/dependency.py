from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    DateTime,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    predecessor_task_id = Column(
        Integer,
        ForeignKey(
            "tasks.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    successor_task_id = Column(
        Integer,
        ForeignKey(
            "tasks.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    dependency_type = Column(
        String(50),
        nullable=False,
        default="finish_to_start"
    )

    lag_days = Column(
        Integer,
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    # ----------------------------------
    # Relationships
    # ----------------------------------

    predecessor = relationship(
        "Task",
        foreign_keys=[predecessor_task_id],
        back_populates="dependencies_before"
    )

    successor = relationship(
        "Task",
        foreign_keys=[successor_task_id],
        back_populates="dependencies_after"
    )

    def __repr__(self):
        return (
            f"<Dependency "
            f"{self.predecessor_task_id} -> "
            f"{self.successor_task_id}>"
        )