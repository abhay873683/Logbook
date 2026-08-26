from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.sql import func

from app.core.database import Base


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    email_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    in_app_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    task_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    message_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    deadline_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    system_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
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