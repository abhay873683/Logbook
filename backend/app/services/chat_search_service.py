from sqlalchemy.orm import Session

from app.models.chat import Message

from app.services.chat_service import (
    validate_chat_access,
)


def search_messages(
    db: Session,
    user_id: int,
    query: str,
    chat_type: str | None = None,
    chat_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
):
    query = query.strip()

    if not query:
        raise ValueError(
            "Search query cannot be empty"
        )

    if chat_type is not None:
        chat_type = (
            chat_type.lower().strip()
        )

        if chat_type not in {
            "channel",
            "group",
            "direct",
        }:
            raise ValueError(
                "Invalid chat type"
            )

    if (
        chat_id is not None
        and chat_type is None
    ):
        raise ValueError(
            "chat_type is required "
            "when chat_id is provided"
        )

    message_query = (
        db.query(Message)
        .filter(
            Message.content.ilike(
                f"%{query}%"
            )
        )
    )

    if chat_type is not None:
        message_query = (
            message_query.filter(
                Message.chat_type
                == chat_type
            )
        )

    if chat_id is not None:
        validate_chat_access(
            db,
            chat_type,
            chat_id,
            user_id,
        )

        message_query = (
            message_query.filter(
                Message.chat_id
                == chat_id
            )
        )

    candidates = (
        message_query
        .order_by(
            Message.created_at.desc()
        )
        .all()
    )

    visible_messages = []

    for message in candidates:
        try:
            validate_chat_access(
                db,
                message.chat_type,
                message.chat_id,
                user_id,
            )

            visible_messages.append(
                message
            )

        except (
            ValueError,
            PermissionError,
        ):
            continue

    return visible_messages[
        skip:skip + limit
    ]
