from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
)

from app.models.user import User

from app.schemas.chat_assistant import (
    ActionItemsResponse,
    ChatSummaryResponse,
    ImportantMessagesResponse,
    SmartReplyRequest,
    SmartReplyResponse,
)

from app.services.chat_assistant_service import (
    detect_important_messages,
    extract_action_items,
    generate_smart_replies,
    summarize_chat,
)


router = APIRouter()


def handle_service_error(exc):
    if isinstance(
        exc,
        PermissionError,
    ):
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    raise HTTPException(
        status_code=404,
        detail=str(exc),
    )


@router.get(
    "/summary/{chat_id}",
    response_model=ChatSummaryResponse,
)
def get_chat_summary(
    chat_id: int,
    chat_type: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return summarize_chat(
            db,
            chat_type,
            chat_id,
            current_user.id,
        )

    except (
        ValueError,
        PermissionError,
    ) as exc:
        handle_service_error(exc)


@router.get(
    "/action-items/{chat_id}",
    response_model=ActionItemsResponse,
)
def get_action_items(
    chat_id: int,
    chat_type: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return extract_action_items(
            db,
            chat_type,
            chat_id,
            current_user.id,
        )

    except (
        ValueError,
        PermissionError,
    ) as exc:
        handle_service_error(exc)


@router.get(
    "/important/{chat_id}",
    response_model=(
        ImportantMessagesResponse
    ),
)
def get_important_messages(
    chat_id: int,
    chat_type: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return detect_important_messages(
            db,
            chat_type,
            chat_id,
            current_user.id,
        )

    except (
        ValueError,
        PermissionError,
    ) as exc:
        handle_service_error(exc)


@router.post(
    "/smart-replies",
    response_model=SmartReplyResponse,
)
def get_smart_replies(
    data: SmartReplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return generate_smart_replies(
            db,
            data.chat_type,
            data.chat_id,
            current_user.id,
            data.max_suggestions,
        )

    except (
        ValueError,
        PermissionError,
    ) as exc:
        handle_service_error(exc)
