from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.services.file_service import get_file_by_id

from app.schemas.file_type import (
    FileClassificationRequest,
    FileClassificationResponse,
    FileOrganizationSuggestionResponse,
    FileTypeResponse,
)
from app.services.file_type_service import (
    classify_file,
    get_all_file_types,
    suggest_file_organization,
)


router = APIRouter()


@router.get(
    "/",
    response_model=list[FileTypeResponse],
)
def list_file_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_file_types(db)


@router.post(
    "/classify",
    response_model=FileClassificationResponse,
)
def classify_file_api(
    data: FileClassificationRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        return classify_file(
            file_name=data.file_name,
            mime_type=data.mime_type,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/classify/{file_id}",
    response_model=FileClassificationResponse,
)
def classify_existing_file_api(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_record = get_file_by_id(
        file_id=file_id,
        db=db,
        user_id=current_user.id,
        role=current_user.role,
    )

    return classify_file(
        file_name=file_record.file_name,
        mime_type=file_record.file_type,
    )


@router.get(
    "/organize/{file_id}",
    response_model=FileOrganizationSuggestionResponse,
)
def suggest_file_organization_api(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_record = get_file_by_id(
        file_id=file_id,
        db=db,
        user_id=current_user.id,
        role=current_user.role,
    )

    return suggest_file_organization(
        db=db,
        file_record=file_record,
        user_id=current_user.id,
    )
