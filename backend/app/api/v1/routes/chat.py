from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.chat import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    GroupCreate,
    GroupResponse,
    DirectConversationResponse,
    MessageCreate,
    MessageResponse,
)

from app.services.chat_service import (
    create_channel,
    get_channels,
    get_channel,
    update_channel,
    join_channel,
    leave_channel,
    create_group,
    get_groups,
    get_group,
    get_or_create_direct_chat,
    get_direct_conversations,
    send_message,
    get_messages,
    mark_message_read,
    delete_message,
)


router = APIRouter(
    tags=["Chat & Collaboration"]
)


# =========================================================
# CHANNELS
# =========================================================

@router.post(
    "/channels/",
    response_model=ChannelResponse,
    status_code=201,
)
def create_new_channel(
    data: ChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_channel(
            db,
            data,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/channels/",
    response_model=list[ChannelResponse],
)
def read_channels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_channels(
        db,
        current_user.id,
    )


@router.get(
    "/channels/{channel_id}",
    response_model=ChannelResponse,
)
def read_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_channel(
            db,
            channel_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.put(
    "/channels/{channel_id}",
    response_model=ChannelResponse,
)
def edit_channel(
    channel_id: int,
    data: ChannelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_channel(
            db,
            channel_id,
            data,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )


@router.post(
    "/channels/{channel_id}/join"
)
def join_existing_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return join_channel(
            db,
            channel_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )


@router.delete(
    "/channels/{channel_id}/leave"
)
def leave_existing_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return leave_channel(
            db,
            channel_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# =========================================================
# GROUPS
# =========================================================

@router.post(
    "/groups/",
    response_model=GroupResponse,
    status_code=201,
)
def create_new_group(
    data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_group(
            db,
            data,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/groups/",
    response_model=list[GroupResponse],
)
def read_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_groups(
        db,
        current_user.id,
    )


@router.get(
    "/groups/{group_id}",
    response_model=GroupResponse,
)
def read_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_group(
            db,
            group_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


# =========================================================
# DIRECT CHAT
# =========================================================

@router.post(
    "/direct/{user_id}",
    response_model=DirectConversationResponse,
)
def create_direct_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_or_create_direct_chat(
            db,
            current_user.id,
            user_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/direct/",
    response_model=list[
        DirectConversationResponse
    ],
)
def read_direct_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_direct_conversations(
        db,
        current_user.id,
    )


# =========================================================
# MESSAGES
# =========================================================

@router.post(
    "/messages/",
    response_model=MessageResponse,
    status_code=201,
)
def create_message(
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return send_message(
            db,
            data,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )


@router.get(
    "/messages/{chat_id}",
    response_model=list[MessageResponse],
)
def read_messages(
    chat_id: int,
    chat_type: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_messages(
            db,
            chat_type,
            chat_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )


@router.put(
    "/messages/{message_id}/read",
    response_model=MessageResponse,
)
def read_message_update(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return mark_message_read(
            db,
            message_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )


@router.delete(
    "/messages/{message_id}"
)
def remove_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_message(
            db,
            message_id,
            current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )