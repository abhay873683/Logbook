from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.dashboard import Dashboard
from app.models.widget import Widget

from app.models.project import Project
from app.models.task import Task, TaskStatusEnum
from app.models.notification import Notification

from app.schemas.dashboard_widget import (
    DashboardCreate,
    DashboardUpdate,
    WidgetCreate,
    WidgetUpdate,
)


ALLOWED_WIDGET_TYPES = {
    "task_summary",
    "project_progress",
    "team_workload",
    "time_tracking",
    "overdue_tasks",
    "upcoming_deadlines",
    "activity_feed",
    "custom_chart",
}


def create_dashboard(
    db: Session,
    user_id: int,
    data: DashboardCreate,
):
    dashboard = Dashboard(
        user_id=user_id,
        name=data.name.strip(),
        description=data.description,
        layout=data.layout or {},
    )

    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)

    return dashboard


def get_dashboards(
    db: Session,
    user_id: int,
):
    return (
        db.query(Dashboard)
        .filter(Dashboard.user_id == user_id)
        .order_by(Dashboard.created_at.desc())
        .all()
    )


def get_dashboard(
    db: Session,
    user_id: int,
    dashboard_id: int,
):
    dashboard = (
        db.query(Dashboard)
        .filter(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == user_id,
        )
        .first()
    )

    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )

    return dashboard


def update_dashboard(
    db: Session,
    user_id: int,
    dashboard_id: int,
    data: DashboardUpdate,
):
    dashboard = get_dashboard(
        db,
        user_id,
        dashboard_id,
    )

    values = data.model_dump(exclude_unset=True)

    for key, value in values.items():
        setattr(dashboard, key, value)

    db.commit()
    db.refresh(dashboard)

    return dashboard


def update_dashboard_layout(
    db: Session,
    user_id: int,
    dashboard_id: int,
    layout: dict,
):
    dashboard = get_dashboard(
        db,
        user_id,
        dashboard_id,
    )

    dashboard.layout = layout

    db.commit()
    db.refresh(dashboard)

    return dashboard


def delete_dashboard(
    db: Session,
    user_id: int,
    dashboard_id: int,
):
    dashboard = get_dashboard(
        db,
        user_id,
        dashboard_id,
    )

    db.query(Widget).filter(
        Widget.dashboard_id == dashboard.id
    ).delete()

    db.delete(dashboard)
    db.commit()

    return {
        "message": "Dashboard deleted successfully"
    }


def create_widget(
    db: Session,
    user_id: int,
    data: WidgetCreate,
):
    get_dashboard(
        db,
        user_id,
        data.dashboard_id,
    )

    if data.widget_type not in ALLOWED_WIDGET_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid widget type",
        )

    widget = Widget(
        dashboard_id=data.dashboard_id,
        user_id=user_id,
        title=data.title,
        widget_type=data.widget_type,
        config=data.config or {},
        size_x=data.size_x,
        size_y=data.size_y,
        position_x=data.position_x,
        position_y=data.position_y,
    )

    db.add(widget)
    db.commit()
    db.refresh(widget)

    return widget


def get_widgets(
    db: Session,
    user_id: int,
):
    return (
        db.query(Widget)
        .filter(Widget.user_id == user_id)
        .order_by(Widget.created_at.desc())
        .all()
    )


def get_widget(
    db: Session,
    user_id: int,
    widget_id: int,
):
    widget = (
        db.query(Widget)
        .filter(
            Widget.id == widget_id,
            Widget.user_id == user_id,
        )
        .first()
    )

    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    return widget


def update_widget(
    db: Session,
    user_id: int,
    widget_id: int,
    data: WidgetUpdate,
):
    widget = get_widget(
        db,
        user_id,
        widget_id,
    )

    values = data.model_dump(exclude_unset=True)

    if "widget_type" in values:
        if values["widget_type"] not in ALLOWED_WIDGET_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid widget type",
            )

    for key, value in values.items():
        setattr(widget, key, value)

    db.commit()
    db.refresh(widget)

    return widget


def delete_widget(
    db: Session,
    user_id: int,
    widget_id: int,
):
    widget = get_widget(
        db,
        user_id,
        widget_id,
    )

    db.delete(widget)
    db.commit()

    return {
        "message": "Widget deleted successfully"
    }


def get_widget_data(
    db: Session,
    user_id: int,
    widget_id: int,
):
    widget = get_widget(
        db,
        user_id,
        widget_id,
    )

    if widget.widget_type == "task_summary":
        total = db.query(func.count(Task.id)).scalar() or 0

        completed = (
            db.query(func.count(Task.id))
            .filter(Task.status == TaskStatusEnum.done)
            .scalar()
            or 0
        )

        return {
            "widget_id": widget.id,
            "type": widget.widget_type,
            "data": {
                "total_tasks": total,
                "completed_tasks": completed,
                "pending_tasks": total - completed,
            },
        }

    if widget.widget_type == "project_progress":
        projects = db.query(Project).all()

        return {
            "widget_id": widget.id,
            "type": widget.widget_type,
            "data": [
                {
                    "project_id": project.id,
                    "name": project.name,
                    "progress": project.progress or 0,
                }
                for project in projects
            ],
        }

    if widget.widget_type == "activity_feed":
        notifications = (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(5)
            .all()
        )

        return {
            "widget_id": widget.id,
            "type": widget.widget_type,
            "data": [
                {
                    "id": item.id,
                    "title": item.title,
                    "message": item.message,
                }
                for item in notifications
            ],
        }

    return {
        "widget_id": widget.id,
        "type": widget.widget_type,
        "data": {},
    }