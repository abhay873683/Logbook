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


class MessageReaction(Base):
    __tablename__ = "message_reactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    message_id = Column(
        Integer,
        ForeignKey(
            "messages.id",
            ondelete="CASCADE",
        ),
        nullable=False,
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

    reaction = Column(
        String(50),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "message_id",
            "user_id",
            "reaction",
            name="uq_message_user_reaction",
        ),
    )
