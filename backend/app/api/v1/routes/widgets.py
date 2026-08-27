from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.dashboard_widget import (
    WidgetCreate,
    WidgetResponse,
    WidgetUpdate,
)

from app.services.dashboard_widget_service import (
    create_widget,
    delete_widget,
    get_widget,
    get_widget_data,
    get_widgets,
    update_widget,
)


router = APIRouter()


@router.post(
    "/",
    response_model=WidgetResponse,
    status_code=201,
)
def add_widget(
    data: WidgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_widget(
        db,
        current_user.id,
        data,
    )


@router.get(
    "/",
    response_model=list[WidgetResponse],
)
def read_widgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_widgets(
        db,
        current_user.id,
    )


@router.get(
    "/{widget_id}",
    response_model=WidgetResponse,
)
def read_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_widget(
        db,
        current_user.id,
        widget_id,
    )


@router.put(
    "/{widget_id}",
    response_model=WidgetResponse,
)
def edit_widget(
    widget_id: int,
    data: WidgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_widget(
        db,
        current_user.id,
        widget_id,
        data,
    )


@router.post("/{widget_id}/data")
def widget_data(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_widget_data(
        db,
        current_user.id,
        widget_id,
    )


@router.delete("/{widget_id}")
def remove_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_widget(
        db,
        current_user.id,
        widget_id,
    )