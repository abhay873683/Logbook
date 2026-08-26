from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User

from app.models.chat import (
    Channel,
    ChannelMember,
    GroupChat,
    GroupMember,
    DirectMessage,
    Message,
)

from app.schemas.chat import (
    ChannelCreate,
    ChannelUpdate,
    GroupCreate,
    MessageCreate,
)


# =========================================================
# USER VALIDATION
# =========================================================

def get_user_or_error(
    db: Session,
    user_id: int,
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    return user


# =========================================================
# CHANNELS
# =========================================================

def create_channel(
    db: Session,
    data: ChannelCreate,
    current_user_id: int,
):
    existing = (
        db.query(Channel)
        .filter(Channel.name == data.name)
        .first()
    )

    if existing:
        raise ValueError(
            "Channel name already exists"
        )

    channel = Channel(
        name=data.name,
        description=data.description,
        channel_type=data.channel_type,
        created_by=current_user_id,
    )

    db.add(channel)
    db.flush()

    member = ChannelMember(
        channel_id=channel.id,
        user_id=current_user_id,
    )

    db.add(member)

    db.commit()
    db.refresh(channel)

    return channel


def get_channels(
    db: Session,
    user_id: int,
):
    return (
        db.query(Channel)
        .join(
            ChannelMember,
            Channel.id
            == ChannelMember.channel_id,
        )
        .filter(
            ChannelMember.user_id
            == user_id
        )
        .all()
    )


def get_channel(
    db: Session,
    channel_id: int,
):
    channel = (
        db.query(Channel)
        .filter(Channel.id == channel_id)
        .first()
    )

    if not channel:
        raise ValueError("Channel not found")

    return channel


def update_channel(
    db: Session,
    channel_id: int,
    data: ChannelUpdate,
    current_user_id: int,
):
    channel = get_channel(
        db,
        channel_id,
    )

    if channel.created_by != current_user_id:
        raise PermissionError(
            "Only channel creator can update channel"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        duplicate = (
            db.query(Channel)
            .filter(
                Channel.name
                == update_data["name"],
                Channel.id != channel_id,
            )
            .first()
        )

        if duplicate:
            raise ValueError(
                "Channel name already exists"
            )

    for key, value in update_data.items():
        setattr(channel, key, value)

    db.commit()
    db.refresh(channel)

    return channel


def join_channel(
    db: Session,
    channel_id: int,
    user_id: int,
):
    channel = get_channel(
        db,
        channel_id,
    )

    existing = (
        db.query(ChannelMember)
        .filter(
            ChannelMember.channel_id
            == channel_id,
            ChannelMember.user_id
            == user_id,
        )
        .first()
    )

    if existing:
        raise ValueError(
            "User already joined this channel"
        )

    # Minimal private-channel protection.
    if channel.channel_type == "private":
        raise PermissionError(
            "Private channel requires invitation"
        )

    member = ChannelMember(
        channel_id=channel_id,
        user_id=user_id,
    )

    db.add(member)
    db.commit()

    return {
        "message": "Channel joined successfully"
    }


def leave_channel(
    db: Session,
    channel_id: int,
    user_id: int,
):
    member = (
        db.query(ChannelMember)
        .filter(
            ChannelMember.channel_id
            == channel_id,
            ChannelMember.user_id
            == user_id,
        )
        .first()
    )

    if not member:
        raise ValueError(
            "User is not a channel member"
        )

    db.delete(member)
    db.commit()

    return {
        "message": "Channel left successfully"
    }


# =========================================================
# GROUP CHAT
# =========================================================

def create_group(
    db: Session,
    data: GroupCreate,
    current_user_id: int,
):
    member_ids = set(data.user_ids)

    member_ids.add(current_user_id)

    if len(member_ids) < 2:
        raise ValueError(
            "Group must contain at least 2 users"
        )

    for user_id in member_ids:
        get_user_or_error(
            db,
            user_id,
        )

    group = GroupChat(
        name=data.name,
        description=data.description,
        created_by=current_user_id,
    )

    db.add(group)
    db.flush()

    for user_id in member_ids:
        db.add(
            GroupMember(
                group_id=group.id,
                user_id=user_id,
            )
        )

    db.commit()
    db.refresh(group)

    return group


def get_groups(
    db: Session,
    user_id: int,
):
    return (
        db.query(GroupChat)
        .join(
            GroupMember,
            GroupChat.id
            == GroupMember.group_id,
        )
        .filter(
            GroupMember.user_id
            == user_id
        )
        .all()
    )


def get_group(
    db: Session,
    group_id: int,
):
    group = (
        db.query(GroupChat)
        .filter(
            GroupChat.id == group_id
        )
        .first()
    )

    if not group:
        raise ValueError(
            "Group not found"
        )

    return group


# =========================================================
# DIRECT CONVERSATION
# =========================================================

def get_or_create_direct_chat(
    db: Session,
    current_user_id: int,
    other_user_id: int,
):
    if current_user_id == other_user_id:
        raise ValueError(
            "Cannot create direct chat with yourself"
        )

    get_user_or_error(
        db,
        other_user_id,
    )

    user1 = min(
        current_user_id,
        other_user_id,
    )

    user2 = max(
        current_user_id,
        other_user_id,
    )

    conversation = (
        db.query(DirectMessage)
        .filter(
            DirectMessage.user1_id == user1,
            DirectMessage.user2_id == user2,
        )
        .first()
    )

    if conversation:
        return conversation

    conversation = DirectMessage(
        user1_id=user1,
        user2_id=user2,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_direct_conversations(
    db: Session,
    user_id: int,
):
    return (
        db.query(DirectMessage)
        .filter(
            or_(
                DirectMessage.user1_id
                == user_id,

                DirectMessage.user2_id
                == user_id,
            )
        )
        .all()
    )


# =========================================================
# CHAT VALIDATION
# =========================================================

def validate_chat_access(
    db: Session,
    chat_type: str,
    chat_id: int,
    user_id: int,
):
    if chat_type == "channel":
        channel = get_channel(
            db,
            chat_id,
        )

        member = (
            db.query(ChannelMember)
            .filter(
                ChannelMember.channel_id
                == channel.id,

                ChannelMember.user_id
                == user_id,
            )
            .first()
        )

        if not member:
            raise PermissionError(
                "User is not a channel member"
            )

    elif chat_type == "group":
        get_group(
            db,
            chat_id,
        )

        member = (
            db.query(GroupMember)
            .filter(
                GroupMember.group_id
                == chat_id,

                GroupMember.user_id
                == user_id,
            )
            .first()
        )

        if not member:
            raise PermissionError(
                "User is not a group member"
            )

    elif chat_type == "direct":
        conversation = (
            db.query(DirectMessage)
            .filter(
                DirectMessage.id == chat_id
            )
            .first()
        )

        if not conversation:
            raise ValueError(
                "Direct conversation not found"
            )

        if user_id not in {
            conversation.user1_id,
            conversation.user2_id,
        }:
            raise PermissionError(
                "User is not part of this conversation"
            )


# =========================================================
# MESSAGES
# =========================================================

def send_message(
    db: Session,
    data: MessageCreate,
    sender_id: int,
):
    validate_chat_access(
        db,
        data.chat_type,
        data.chat_id,
        sender_id,
    )

    message = Message(
        chat_type=data.chat_type,
        chat_id=data.chat_id,
        sender_id=sender_id,
        content=data.content,
        file_url=data.file_url,
        is_read=False,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_messages(
    db: Session,
    chat_type: str,
    chat_id: int,
    user_id: int,
):
    validate_chat_access(
        db,
        chat_type,
        chat_id,
        user_id,
    )

    return (
        db.query(Message)
        .filter(
            Message.chat_type
            == chat_type,

            Message.chat_id
            == chat_id,
        )
        .order_by(
            Message.created_at.asc()
        )
        .all()
    )


def mark_message_read(
    db: Session,
    message_id: int,
    user_id: int,
):
    message = (
        db.query(Message)
        .filter(
            Message.id == message_id
        )
        .first()
    )

    if not message:
        raise ValueError(
            "Message not found"
        )

    validate_chat_access(
        db,
        message.chat_type,
        message.chat_id,
        user_id,
    )

    if message.sender_id == user_id:
        raise ValueError(
            "Sender cannot mark own message as read"
        )

    message.is_read = True

    db.commit()
    db.refresh(message)

    return message


def delete_message(
    db: Session,
    message_id: int,
    user_id: int,
):
    message = (
        db.query(Message)
        .filter(
            Message.id == message_id
        )
        .first()
    )

    if not message:
        raise ValueError(
            "Message not found"
        )

    if message.sender_id != user_id:
        raise PermissionError(
            "Only sender can delete this message"
        )

    db.delete(message)
    db.commit()

    return {
        "message": "Message deleted successfully"
    }