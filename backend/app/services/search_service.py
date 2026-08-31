from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.file import File
from app.models.file_share import FileShare
from app.models.project import Project
from app.models.project_user import ProjectUser
from app.models.task import Task


PRIVILEGED_ROLES = {
    "admin",
    "super_admin",
    "manager",
}

RESOURCE_TYPES = {
    "all",
    "project",
    "task",
    "file",
    "comment",
}


def _normalize_role(role) -> str:
    if role is None:
        return ""

    value = getattr(role, "value", role)

    return str(value).strip().lower()


def _snippet(value, length=180):
    if not value:
        return None

    text = " ".join(str(value).split())

    if len(text) <= length:
        return text

    return text[:length].rstrip() + "..."


def _score(query, title, description=None):
    needle = query.lower()

    title_value = (title or "").lower()
    description_value = (description or "").lower()

    if title_value == needle:
        return 1.0

    if title_value.startswith(needle):
        return 0.95

    if needle in title_value:
        return 0.90

    if needle in description_value:
        return 0.75

    return 0.50


def _accessible_project_ids(
    db: Session,
    user_id: int,
    role,
):
    normalized_role = _normalize_role(role)

    query = db.query(Project.id).filter(
        Project.is_active == True
    )

    if normalized_role in PRIVILEGED_ROLES:
        return query

    member_project_ids = (
        db.query(ProjectUser.project_id)
        .filter(ProjectUser.user_id == user_id)
    )

    return query.filter(
        or_(
            Project.created_by == user_id,
            Project.id.in_(member_project_ids),
        )
    )


def _search_projects(
    db,
    user_id,
    role,
    query,
):
    project_ids = _accessible_project_ids(
        db,
        user_id,
        role,
    )

    rows = (
        db.query(Project)
        .filter(
            Project.id.in_(project_ids),
            or_(
                Project.name.ilike(f"%{query}%"),
                Project.description.ilike(f"%{query}%"),
            ),
        )
        .all()
    )

    return [
        {
            "resource_type": "project",
            "resource_id": row.id,
            "title": row.name,
            "snippet": _snippet(row.description),
            "relevance": _score(
                query,
                row.name,
                row.description,
            ),
            "metadata": {
                "status": row.status,
                "progress": row.progress,
                "company_id": row.company_id,
                "team_id": row.team_id,
            },
        }
        for row in rows
    ]


def _search_tasks(
    db,
    user_id,
    role,
    query,
):
    project_ids = _accessible_project_ids(
        db,
        user_id,
        role,
    )

    rows = (
        db.query(Task)
        .filter(
            Task.is_active == True,
            Task.project_id.in_(project_ids),
            or_(
                Task.name.ilike(f"%{query}%"),
                Task.description.ilike(f"%{query}%"),
            ),
        )
        .all()
    )

    return [
        {
            "resource_type": "task",
            "resource_id": row.id,
            "title": row.name,
            "snippet": _snippet(row.description),
            "relevance": _score(
                query,
                row.name,
                row.description,
            ),
            "metadata": {
                "project_id": row.project_id,
                "status": (
                    row.status.value
                    if hasattr(row.status, "value")
                    else str(row.status)
                ),
                "priority": (
                    row.priority.value
                    if hasattr(row.priority, "value")
                    else str(row.priority)
                ),
                "progress": row.progress,
            },
        }
        for row in rows
    ]


def _search_files(
    db,
    user_id,
    role,
    query,
):
    normalized_role = _normalize_role(role)

    file_query = db.query(File).filter(
        File.is_active == True,
        File.deleted_at.is_(None),
        File.file_name.ilike(f"%{query}%"),
    )

    if normalized_role not in PRIVILEGED_ROLES:
        shared_ids = (
            db.query(FileShare.file_id)
            .filter(
                FileShare.shared_with == user_id,
                FileShare.is_active == True,
            )
        )

        file_query = file_query.filter(
            or_(
                File.uploaded_by == user_id,
                File.id.in_(shared_ids),
            )
        )

    rows = file_query.all()

    return [
        {
            "resource_type": "file",
            "resource_id": row.id,
            "title": row.file_name,
            "snippet": row.file_type,
            "relevance": _score(
                query,
                row.file_name,
            ),
            "metadata": {
                "task_id": row.task_id,
                "folder_id": row.folder_id,
                "file_type": row.file_type,
                "file_size": row.file_size,
            },
        }
        for row in rows
    ]


def _search_comments(
    db,
    user_id,
    role,
    query,
):
    project_ids = _accessible_project_ids(
        db,
        user_id,
        role,
    )

    rows = (
        db.query(Comment)
        .join(
            Task,
            Comment.task_id == Task.id,
        )
        .filter(
            Task.is_active == True,
            Task.project_id.in_(project_ids),
            Comment.comment.ilike(f"%{query}%"),
        )
        .all()
    )

    return [
        {
            "resource_type": "comment",
            "resource_id": row.id,
            "title": f"Comment #{row.id}",
            "snippet": _snippet(row.comment),
            "relevance": (
                0.85
                if query.lower()
                in (row.comment or "").lower()
                else 0.50
            ),
            "metadata": {
                "task_id": row.task_id,
                "user_id": row.user_id,
            },
        }
        for row in rows
    ]


def search_all(
    db: Session,
    user_id: int,
    role,
    query: str,
    resource_type: str = "all",
    skip: int = 0,
    limit: int = 20,
):
    clean_query = (query or "").strip()

    if not clean_query:
        raise ValueError(
            "Search query cannot be empty"
        )

    clean_type = (
        resource_type or "all"
    ).strip().lower()

    if clean_type not in RESOURCE_TYPES:
        raise ValueError(
            "Invalid resource type"
        )

    results = []

    if clean_type in {"all", "project"}:
        results.extend(
            _search_projects(
                db,
                user_id,
                role,
                clean_query,
            )
        )

    if clean_type in {"all", "task"}:
        results.extend(
            _search_tasks(
                db,
                user_id,
                role,
                clean_query,
            )
        )

    if clean_type in {"all", "file"}:
        results.extend(
            _search_files(
                db,
                user_id,
                role,
                clean_query,
            )
        )

    if clean_type in {"all", "comment"}:
        results.extend(
            _search_comments(
                db,
                user_id,
                role,
                clean_query,
            )
        )

    results.sort(
        key=lambda item: (
            item["relevance"],
            item["resource_id"],
        ),
        reverse=True,
    )

    total = len(results)

    return {
        "query": clean_query,
        "resource_type": clean_type,
        "total": total,
        "skip": skip,
        "limit": limit,
        "results": results[
            skip:skip + limit
        ],
    }
