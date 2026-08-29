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
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # --------------------------------------------------------
    # CHANNEL PREFERENCES
    # --------------------------------------------------------

    email_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    push_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    in_app_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    # --------------------------------------------------------
    # CATEGORY PREFERENCES
    # --------------------------------------------------------

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

    security_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    approval_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    general_notifications = Column(
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

    def __repr__(self):
        return (
            "<NotificationPreference("
            f"id={self.id}, "
            f"user_id={self.user_id}"
            ")>"
        )
