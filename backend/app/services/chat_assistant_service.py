import re

from sqlalchemy.orm import Session

from app.models.chat import Message

from app.services.chat_service import (
    validate_chat_access,
)


ACTION_KEYWORDS = (
    "please",
    "need to",
    "todo",
    "to do",
    "follow up",
    "follow-up",
    "complete",
    "finish",
    "send",
    "review",
    "update",
    "check",
    "deadline",
    "assign",
)


IMPORTANT_KEYWORDS = (
    "urgent",
    "important",
    "asap",
    "deadline",
    "critical",
    "priority",
    "blocked",
    "issue",
    "error",
    "failed",
    "failure",
)


QUESTION_WORDS = (
    "what",
    "when",
    "where",
    "why",
    "who",
    "how",
    "can",
    "could",
    "should",
    "would",
    "is",
    "are",
    "do",
    "does",
)


def _get_accessible_messages(
    db: Session,
    chat_type: str,
    chat_id: int,
    user_id: int,
    limit: int = 100,
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
            Message.chat_type == chat_type,
            Message.chat_id == chat_id,
        )
        .order_by(
            Message.created_at.desc()
        )
        .limit(limit)
        .all()[::-1]
    )


def _clean_text(value: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        value or "",
    ).strip()


def summarize_chat(
    db: Session,
    chat_type: str,
    chat_id: int,
    user_id: int,
):
    messages = _get_accessible_messages(
        db,
        chat_type,
        chat_id,
        user_id,
        limit=100,
    )

    if not messages:
        summary = (
            "No messages are available "
            "for this conversation."
        )

        participants = []

    else:
        participants = sorted(
            {
                message.sender_id
                for message in messages
            }
        )

        recent = messages[-5:]

        snippets = []

        for message in recent:
            content = _clean_text(
                message.content
            )

            if len(content) > 140:
                content = (
                    content[:137] + "..."
                )

            if content:
                snippets.append(content)

        if snippets:
            summary = (
                "Recent discussion: "
                + " | ".join(snippets)
            )
        else:
            summary = (
                "Recent messages contain "
                "no text content."
            )

    return {
        "chat_type": chat_type,
        "chat_id": chat_id,
        "message_count": len(messages),
        "summary": summary,
        "participants": participants,
    }


def extract_action_items(
    db: Session,
    chat_type: str,
    chat_id: int,
    user_id: int,
):
    messages = _get_accessible_messages(
        db,
        chat_type,
        chat_id,
        user_id,
        limit=200,
    )

    items = []

    for message in messages:
        content = _clean_text(
            message.content
        )

        lowered = content.lower()

        if any(
            keyword in lowered
            for keyword in ACTION_KEYWORDS
        ):
            items.append(
                {
                    "message_id": message.id,
                    "sender_id": (
                        message.sender_id
                    ),
                    "content": content,
                }
            )

    return {
        "chat_type": chat_type,
        "chat_id": chat_id,
        "action_items": items,
    }


def detect_important_messages(
    db: Session,
    chat_type: str,
    chat_id: int,
    user_id: int,
):
    messages = _get_accessible_messages(
        db,
        chat_type,
        chat_id,
        user_id,
        limit=200,
    )

    important = []

    for message in messages:
        content = _clean_text(
            message.content
        )

        lowered = content.lower()

        score = 0

        for keyword in IMPORTANT_KEYWORDS:
            if keyword in lowered:
                score += 2

        if "!" in content:
            score += 1

        if content.isupper() and content:
            score += 1

        if score > 0:
            important.append(
                {
                    "message_id": message.id,
                    "sender_id": (
                        message.sender_id
                    ),
                    "content": content,
                    "importance_score": score,
                }
            )

    important.sort(
        key=lambda item: (
            item["importance_score"],
            item["message_id"],
        ),
        reverse=True,
    )

    return {
        "chat_type": chat_type,
        "chat_id": chat_id,
        "messages": important[:20],
    }


def generate_smart_replies(
    db: Session,
    chat_type: str,
    chat_id: int,
    user_id: int,
    max_suggestions: int = 3,
):
    messages = _get_accessible_messages(
        db,
        chat_type,
        chat_id,
        user_id,
        limit=20,
    )

    if not messages:
        suggestions = [
            "Hello!",
            "How can I help?",
            "Let's get started.",
        ]

        return {
            "chat_type": chat_type,
            "chat_id": chat_id,
            "suggestions": (
                suggestions[
                    :max_suggestions
                ]
            ),
        }

    latest = messages[-1]

    content = _clean_text(
        latest.content
    )

    lowered = content.lower()

    suggestions = []

    if "thank" in lowered:
        suggestions.extend(
            [
                "You're welcome!",
                "Happy to help.",
                "Anytime!",
            ]
        )

    elif any(
        keyword in lowered
        for keyword in (
            "urgent",
            "asap",
            "critical",
            "blocked",
        )
    ):
        suggestions.extend(
            [
                "I'm checking this now.",
                "I'll prioritize this.",
                "I'll update you shortly.",
            ]
        )

    elif (
        content.endswith("?")
        or any(
            lowered.startswith(
                word + " "
            )
            for word in QUESTION_WORDS
        )
    ):
        suggestions.extend(
            [
                "Yes, I'll check and confirm.",
                "I'll look into it.",
                "Let me verify the details.",
            ]
        )

    elif any(
        keyword in lowered
        for keyword in ACTION_KEYWORDS
    ):
        suggestions.extend(
            [
                "I'll take care of it.",
                "I'll work on this.",
                "I'll share an update soon.",
            ]
        )

    else:
        suggestions.extend(
            [
                "Got it.",
                "Thanks for the update.",
                "Understood.",
            ]
        )

    unique = []

    for suggestion in suggestions:
        if suggestion not in unique:
            unique.append(suggestion)

    return {
        "chat_type": chat_type,
        "chat_id": chat_id,
        "suggestions": (
            unique[:max_suggestions]
        ),
    }
