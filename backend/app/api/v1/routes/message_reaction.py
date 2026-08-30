from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.message_reaction import (
    MessageReactionCreate,
    MessageReactionResponse,
    MessageReactionDeleteResponse,
)

from app.services.message_reaction_service import (
    add_message_reaction,
    get_message_reactions,
    remove_message_reaction,
)


router = APIRouter()


@router.post(
    "/{message_id}/reactions/",
    response_model=MessageReactionResponse,
    status_code=201,
)
def create_reaction(
    message_id: int,
    data: MessageReactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return add_message_reaction(
            db,
            message_id,
            data,
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


@router.get(
    "/{message_id}/reactions/",
    response_model=list[
        MessageReactionResponse
    ],
)
def read_reactions(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return get_message_reactions(
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


@router.delete(
    "/{message_id}/reactions/{reaction_id}",
    response_model=(
        MessageReactionDeleteResponse
    ),
)
def delete_reaction(
    message_id: int,
    reaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return remove_message_reaction(
            db,
            message_id,
            reaction_id,
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
