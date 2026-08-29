from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


# =========================================================
# CHANNEL
# =========================================================

class ChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    channel_type: str = "public"

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Channel name cannot be empty"
            )

        return value

    @field_validator("channel_type")
    @classmethod
    def validate_channel_type(cls, value):
        value = value.lower().strip()

        if value not in {
            "public",
            "private",
        }:
            raise ValueError(
                "Channel type must be public or private"
            )

        return value


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    channel_type: Optional[str] = None


class ChannelResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    channel_type: str
    created_by: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# GROUP
# =========================================================

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None

    user_ids: list[int] = Field(
        default_factory=list
    )

    @field_validator("name")
    @classmethod
    def validate_group_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Group name cannot be empty"
            )

        return value


class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_by: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# DIRECT CHAT
# =========================================================

class DirectMessageCreate(BaseModel):
    user_id: int


class DirectConversationResponse(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# MESSAGE
# =========================================================

class MessageCreate(BaseModel):
    chat_type: str
    chat_id: int
    content: str
    file_url: Optional[str] = None

    @field_validator("chat_type")
    @classmethod
    def validate_chat_type(cls, value):
        value = value.lower().strip()

        if value not in {
            "channel",
            "group",
            "direct",
        }:
            raise ValueError(
                "chat_type must be channel, group or direct"
            )

        return value

    @field_validator("content")
    @classmethod
    def validate_content(cls, value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Message cannot be empty"
            )

        return value


class MessageResponse(BaseModel):
    id: int
    chat_type: str
    chat_id: int
    sender_id: int
    content: str
    file_url: Optional[str]
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UnreadMessageCountResponse(BaseModel):
    chat_type: str
    chat_id: int
    unread_count: int


class MarkAllMessagesReadResponse(BaseModel):
    chat_type: str
    chat_id: int
    marked_read: int


class MessageStatsResponse(BaseModel):
    total_messages: int
    sent_messages: int
    unread_messages: int
