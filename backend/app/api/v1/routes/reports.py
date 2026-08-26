from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.services.report_service import (
    get_summary_report,
    get_department_summary,
    get_all_project_reports,
    get_project_report,
    get_project_tasks_report,
    get_all_task_reports,
    get_task_status_distribution,
    get_overdue_tasks,
    get_user_productivity,
    get_user_report,
    get_reports_dashboard,
)


router = APIRouter(
    tags=["Reports & Analytics"]
)


@router.get("/summary")
def summary_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_summary_report(db)


@router.get("/summary/department/{department_id}")
def department_summary(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_department_summary(
        db,
        department_id,
    )


@router.get("/projects")
def project_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_project_reports(db)


@router.get("/projects/{project_id}")
def project_report(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_project_report(
            db,
            project_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("/projects/{project_id}/tasks")
def project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_project_tasks_report(
            db,
            project_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("/tasks")
def task_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_task_reports(db)


@router.get("/tasks/status")
def task_status_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_task_status_distribution(db)


@router.get("/tasks/overdue")
def overdue_tasks_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_overdue_tasks(db)


@router.get("/users/productivity")
def user_productivity_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_productivity(db)


@router.get("/users/{user_id}")
def user_report(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_user_report(
            db,
            user_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("/dashboard/overview")
def reports_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_reports_dashboard(db)