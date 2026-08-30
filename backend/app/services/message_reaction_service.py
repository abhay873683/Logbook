from sqlalchemy.orm import Session

from app.models.chat import Message
from app.models.message_reaction import (
    MessageReaction,
)

from app.schemas.message_reaction import (
    MessageReactionCreate,
)

from app.services.chat_service import (
    validate_chat_access,
)


def get_message_or_error(
    db: Session,
    message_id: int,
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

    return message


def add_message_reaction(
    db: Session,
    message_id: int,
    data: MessageReactionCreate,
    user_id: int,
):
    message = get_message_or_error(
        db,
        message_id,
    )

    validate_chat_access(
        db,
        message.chat_type,
        message.chat_id,
        user_id,
    )

    existing = (
        db.query(MessageReaction)
        .filter(
            MessageReaction.message_id
            == message_id,
            MessageReaction.user_id
            == user_id,
            MessageReaction.reaction
            == data.reaction,
        )
        .first()
    )

    if existing:
        return existing

    reaction = MessageReaction(
        message_id=message_id,
        user_id=user_id,
        reaction=data.reaction,
    )

    db.add(reaction)
    db.commit()
    db.refresh(reaction)

    return reaction


def get_message_reactions(
    db: Session,
    message_id: int,
    user_id: int,
):
    message = get_message_or_error(
        db,
        message_id,
    )

    validate_chat_access(
        db,
        message.chat_type,
        message.chat_id,
        user_id,
    )

    return (
        db.query(MessageReaction)
        .filter(
            MessageReaction.message_id
            == message_id
        )
        .order_by(
            MessageReaction.created_at.asc()
        )
        .all()
    )


def remove_message_reaction(
    db: Session,
    message_id: int,
    reaction_id: int,
    user_id: int,
):
    message = get_message_or_error(
        db,
        message_id,
    )

    validate_chat_access(
        db,
        message.chat_type,
        message.chat_id,
        user_id,
    )

    reaction = (
        db.query(MessageReaction)
        .filter(
            MessageReaction.id
            == reaction_id,
            MessageReaction.message_id
            == message_id,
        )
        .first()
    )

    if not reaction:
        raise ValueError(
            "Reaction not found"
        )

    if reaction.user_id != user_id:
        raise PermissionError(
            "Only reaction owner can remove it"
        )

    db.delete(reaction)
    db.commit()

    return {
        "message": (
            "Reaction removed successfully"
        )
    }
