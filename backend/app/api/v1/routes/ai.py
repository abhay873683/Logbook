from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.ai import (
    AISessionCreate,
    AISessionUpdate,
    AISessionResponse,
    AIMessageCreate,
    AIMessageResponse,
    AISuggestionCreate,
    AISuggestionResponse,
)

from app.services.ai_service import (
    create_ai_session,
    get_ai_sessions,
    get_session_or_error,
    update_ai_session,
    delete_ai_session,
    get_session_messages,
    send_ai_message,
    summarize_session,
    create_ai_suggestion,
)


router = APIRouter()


# =========================================================
# CREATE AI SESSION
# =========================================================

@router.post(
    "/sessions/",
    response_model=AISessionResponse,
    status_code=201,
)
def create_session(
    data: AISessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_ai_session(
        db,
        current_user.id,
        data,
    )


# =========================================================
# GET AI SESSIONS
# =========================================================

@router.get(
    "/sessions/",
    response_model=list[AISessionResponse],
)
def read_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_ai_sessions(
        db,
        current_user.id,
    )


# =========================================================
# GET SINGLE AI SESSION
# =========================================================

@router.get(
    "/sessions/{session_id}",
    response_model=AISessionResponse,
)
def read_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_session_or_error(
            db,
            session_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


# =========================================================
# UPDATE AI SESSION
# =========================================================

@router.put(
    "/sessions/{session_id}",
    response_model=AISessionResponse,
)
def update_session(
    session_id: int,
    data: AISessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_ai_session(
            db,
            session_id,
            current_user.id,
            data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# =========================================================
# DELETE AI SESSION
# =========================================================

@router.delete(
    "/sessions/{session_id}"
)
def remove_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_ai_session(
            db,
            session_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


# =========================================================
# SEND MESSAGE TO AI
# =========================================================

@router.post(
    "/sessions/{session_id}/messages/",
    response_model=AIMessageResponse,
    status_code=201,
)
def send_message(
    session_id: int,
    data: AIMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_ai_message(
            db,
            session_id,
            current_user.id,
            data.message,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


# =========================================================
# GET SESSION MESSAGES
# =========================================================

@router.get(
    "/sessions/{session_id}/messages/",
    response_model=list[AIMessageResponse],
)
def read_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_session_messages(
            db,
            session_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


# =========================================================
# SUMMARIZE SESSION
# =========================================================

@router.post(
    "/sessions/{session_id}/summarize/"
)
def summarize(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return summarize_session(
            db,
            session_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


# =========================================================
# AI SUGGESTIONS
# =========================================================

@router.post(
    "/suggestions/",
    response_model=AISuggestionResponse,
    status_code=201,
)
def suggestions(
    data: AISuggestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_ai_suggestion(
            db,
            current_user.id,
            data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )