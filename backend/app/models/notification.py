from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    type = Column(
        String(50),
        default="info",
        nullable=False,
        index=True,
    )

    priority = Column(
        String(20),
        default="normal",
        nullable=False,
        index=True,
    )

    category = Column(
        String(50),
        default="general",
        nullable=False,
        index=True,
    )

    source = Column(
        String(100),
        default="system",
        nullable=False,
        index=True,
    )

    data = Column(
        JSON,
        nullable=True,
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship(
        "User",
        back_populates="notifications",
    )

    def __repr__(self):
        return (
            f"<Notification("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"priority='{self.priority}', "
            f"title='{self.title}')>"
        )
