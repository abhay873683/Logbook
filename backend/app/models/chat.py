from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.sql import func

from app.core.database import Base


# =========================================================
# CHANNEL
# =========================================================

class Channel(Base):
    __tablename__ = "channels"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    channel_type = Column(
        String(20),
        nullable=False,
        default="public",
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


# =========================================================
# CHANNEL MEMBER
# =========================================================

class ChannelMember(Base):
    __tablename__ = "channel_members"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    channel_id = Column(
        Integer,
        ForeignKey(
            "channels.id",
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

    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "channel_id",
            "user_id",
            name="uq_channel_member",
        ),
    )


# =========================================================
# GROUP CHAT
# =========================================================

class GroupChat(Base):
    __tablename__ = "group_chats"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


# =========================================================
# GROUP MEMBER
# =========================================================

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    group_id = Column(
        Integer,
        ForeignKey(
            "group_chats.id",
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

    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "user_id",
            name="uq_group_member",
        ),
    )


# =========================================================
# DIRECT MESSAGE CONVERSATION
# =========================================================

class DirectMessage(Base):
    __tablename__ = "direct_messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user1_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    user2_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user1_id",
            "user2_id",
            name="uq_direct_conversation",
        ),
    )


# =========================================================
# MESSAGE
# =========================================================

class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # channel / group / direct
    chat_type = Column(
        String(20),
        nullable=False,
    )

    # Channel.id / GroupChat.id / DirectMessage.id
    chat_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    sender_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    file_url = Column(
        String(500),
        nullable=True,
    )

    is_read = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )