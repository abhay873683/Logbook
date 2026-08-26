from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    action = Column(
        String(100),
        nullable=False,
    )

    module = Column(
        String(100),
        nullable=False,
    )

    module_id = Column(
        Integer,
        nullable=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    ip_address = Column(
        String(50),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = relationship(
        "User",
        back_populates="activity_logs",
    )

    def __repr__(self):
        return (
            f"<ActivityLog("
            f"id={self.id}, "
            f"action='{self.action}', "
            f"module='{self.module}'"
            f")>"
        )