import os

from sqlalchemy.orm import Session

from app.models.ai import (
    AIChatSession,
    AIMessage,
    AISuggestion,
)

from app.schemas.ai import (
    AISessionCreate,
    AISessionUpdate,
    AISuggestionCreate,
)


# =========================================================
# GET SESSION OR ERROR
# =========================================================

def get_session_or_error(
    db: Session,
    session_id: int,
    user_id: int,
):
    session = (
        db.query(AIChatSession)
        .filter(
            AIChatSession.id == session_id,
            AIChatSession.user_id == user_id,
        )
        .first()
    )

    if not session:
        raise ValueError(
            "AI session not found"
        )

    return session


# =========================================================
# CREATE AI SESSION
# =========================================================

def create_ai_session(
    db: Session,
    user_id: int,
    data: AISessionCreate,
):
    title = data.title.strip()

    if not title:
        title = "New AI Chat"

    session = AIChatSession(
        user_id=user_id,
        title=title,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


# =========================================================
# GET AI SESSIONS
# =========================================================

def get_ai_sessions(
    db: Session,
    user_id: int,
):
    return (
        db.query(AIChatSession)
        .filter(
            AIChatSession.user_id == user_id
        )
        .order_by(
            AIChatSession.updated_at.desc()
        )
        .all()
    )


# =========================================================
# UPDATE AI SESSION
# =========================================================

def update_ai_session(
    db: Session,
    session_id: int,
    user_id: int,
    data: AISessionUpdate,
):
    session = get_session_or_error(
        db,
        session_id,
        user_id,
    )

    title = data.title.strip()

    if not title:
        raise ValueError(
            "Session title cannot be empty"
        )

    session.title = title

    db.commit()
    db.refresh(session)

    return session


# =========================================================
# DELETE AI SESSION
# =========================================================

def delete_ai_session(
    db: Session,
    session_id: int,
    user_id: int,
):
    session = get_session_or_error(
        db,
        session_id,
        user_id,
    )

    db.delete(session)
    db.commit()

    return {
        "message": "AI session deleted successfully"
    }


# =========================================================
# GET SESSION MESSAGES
# =========================================================

def get_session_messages(
    db: Session,
    session_id: int,
    user_id: int,
):
    get_session_or_error(
        db,
        session_id,
        user_id,
    )

    return (
        db.query(AIMessage)
        .filter(
            AIMessage.session_id == session_id
        )
        .order_by(
            AIMessage.created_at.asc()
        )
        .all()
    )


# =========================================================
# GENERATE AI RESPONSE
# =========================================================

def generate_ai_reply(
    prompt: str,
    history: list[AIMessage],
):
    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.4-mini",
    )

    # -----------------------------------------------------
    # Development fallback
    # -----------------------------------------------------
    # API key na hone par bhi Day 36 endpoints test ho sakein.
    # -----------------------------------------------------

    if not api_key:
        return (
            "AI development mode: "
            f"I received your message: {prompt}"
        )

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key
        )

        conversation = []

        for item in history[-10:]:
            conversation.append(
                f"{item.role}: {item.content}"
            )

        conversation.append(
            f"user: {prompt}"
        )

        response = client.responses.create(
            model=model,
            instructions=(
                "You are TreeFlow AI, an assistant for "
                "project management, task planning, "
                "productivity, summaries, reports, "
                "collaboration and workflow guidance. "
                "Provide clear, practical and concise answers."
            ),
            input="\n".join(conversation),
        )

        reply = response.output_text

        if not reply:
            raise RuntimeError(
                "AI returned an empty response"
            )

        return reply.strip()

    except Exception as exc:
        raise RuntimeError(
            f"AI service error: {exc}"
        ) from exc


# =========================================================
# SEND AI MESSAGE
# =========================================================

def send_ai_message(
    db: Session,
    session_id: int,
    user_id: int,
    prompt: str,
):
    session = get_session_or_error(
        db,
        session_id,
        user_id,
    )

    prompt = prompt.strip()

    if not prompt:
        raise ValueError(
            "Message cannot be empty"
        )

    # -----------------------------------------------------
    # Existing history
    # -----------------------------------------------------

    history = get_session_messages(
        db,
        session_id,
        user_id,
    )

    # -----------------------------------------------------
    # Save user message
    # -----------------------------------------------------

    user_message = AIMessage(
        session_id=session.id,
        role="user",
        content=prompt,
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # -----------------------------------------------------
    # Generate AI reply
    # -----------------------------------------------------

    reply = generate_ai_reply(
        prompt,
        history,
    )

    # -----------------------------------------------------
    # Save assistant reply
    # -----------------------------------------------------

    assistant_message = AIMessage(
        session_id=session.id,
        role="assistant",
        content=reply,
    )

    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return assistant_message


# =========================================================
# SUMMARIZE AI SESSION
# =========================================================

def summarize_session(
    db: Session,
    session_id: int,
    user_id: int,
):
    messages = get_session_messages(
        db,
        session_id,
        user_id,
    )

    if not messages:
        raise ValueError(
            "Session has no messages"
        )

    conversation = "\n".join(
        (
            f"{message.role}: "
            f"{message.content}"
        )
        for message in messages
    )

    prompt = (
        "Summarize the following TreeFlow conversation "
        "clearly and briefly. Include important decisions, "
        "tasks and useful next steps when relevant:\n\n"
        f"{conversation}"
    )

    summary = generate_ai_reply(
        prompt,
        [],
    )

    return {
        "session_id": session_id,
        "summary": summary,
    }


# =========================================================
# CREATE AI SUGGESTION
# =========================================================

def create_ai_suggestion(
    db: Session,
    user_id: int,
    data: AISuggestionCreate,
):
    input_text = data.input_text.strip()

    if not input_text:
        raise ValueError(
            "Input text cannot be empty"
        )

    suggestion_type = (
        data.suggestion_type.strip()
        if data.suggestion_type
        else "task"
    )

    prompt = (
        f"Create a {suggestion_type} suggestion "
        "for the following TreeFlow work-management context. "
        "Make the suggestion practical and actionable:\n\n"
        f"{input_text}"
    )

    output = generate_ai_reply(
        prompt,
        [],
    )

    suggestion = AISuggestion(
        user_id=user_id,
        suggestion_type=suggestion_type,
        input_text=input_text,
        output_text=output,
    )

    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)

    return suggestion