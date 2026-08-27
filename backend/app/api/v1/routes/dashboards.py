from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.dashboard_widget import (
    DashboardCreate,
    DashboardLayoutUpdate,
    DashboardResponse,
    DashboardUpdate,
)

from app.services.dashboard_widget_service import (
    create_dashboard,
    delete_dashboard,
    get_dashboard,
    get_dashboards,
    update_dashboard,
    update_dashboard_layout,
)


router = APIRouter()


@router.post(
    "/",
    response_model=DashboardResponse,
    status_code=201,
)
def add_dashboard(
    data: DashboardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_dashboard(
        db,
        current_user.id,
        data,
    )


@router.get(
    "/",
    response_model=list[DashboardResponse],
)
def read_dashboards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_dashboards(
        db,
        current_user.id,
    )


@router.get(
    "/{dashboard_id}",
    response_model=DashboardResponse,
)
def read_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_dashboard(
        db,
        current_user.id,
        dashboard_id,
    )


@router.put(
    "/{dashboard_id}",
    response_model=DashboardResponse,
)
def edit_dashboard(
    dashboard_id: int,
    data: DashboardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_dashboard(
        db,
        current_user.id,
        dashboard_id,
        data,
    )


@router.put(
    "/{dashboard_id}/layout",
    response_model=DashboardResponse,
)
def save_dashboard_layout(
    dashboard_id: int,
    data: DashboardLayoutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_dashboard_layout(
        db,
        current_user.id,
        dashboard_id,
        data.layout,
    )


@router.delete("/{dashboard_id}")
def remove_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_dashboard(
        db,
        current_user.id,
        dashboard_id,
    )