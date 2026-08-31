from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.file import File
from app.models.file_share import FileShare
from app.models.project import Project
from app.models.project_user import ProjectUser
from app.models.task import (
    Task,
    TaskPriorityEnum,
    TaskStatusEnum,
)


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

SORT_OPTIONS = {
    "relevance",
    "newest",
    "oldest",
}

PROJECT_STATUSES = {
    "planned",
    "in progress",
    "on hold",
    "completed",
    "cancelled",
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


def _terms(query: str):
    parts = [
        part.lower()
        for part in query.split()
        if len(part.strip()) >= 2
    ]

    return list(dict.fromkeys(parts))


def _text_filter(query, *columns):
    conditions = []

    clean_query = query.strip()

    for column in columns:
        conditions.append(
            column.ilike(f"%{clean_query}%")
        )

    for term in _terms(clean_query):
        for column in columns:
            conditions.append(
                column.ilike(f"%{term}%")
            )

    return or_(*conditions)


def _score(query, title, description=None):
    needle = query.lower().strip()

    title_value = (title or "").lower()
    description_value = (
        description or ""
    ).lower()

    if title_value == needle:
        return 1.0

    if title_value.startswith(needle):
        return 0.97

    if needle in title_value:
        return 0.94

    if needle in description_value:
        return 0.86

    terms = _terms(needle)

    if not terms:
        return 0.50

    title_hits = sum(
        1 for term in terms
        if term in title_value
    )

    description_hits = sum(
        1 for term in terms
        if term in description_value
    )

    total_terms = len(terms)

    title_coverage = (
        title_hits / total_terms
    )

    description_coverage = (
        description_hits / total_terms
    )

    if title_hits:
        return round(
            0.65 + (0.25 * title_coverage),
            4,
        )

    if description_hits:
        return round(
            0.55
            + (
                0.25
                * description_coverage
            ),
            4,
        )

    return 0.50


def _parse_enum(value, enum_class, label):
    if value is None:
        return None

    normalized = (
        str(value)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    for member in enum_class:
        member_name = (
            member.name
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        member_value = (
            str(member.value)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        if normalized in {
            member_name,
            member_value,
        }:
            return member

    allowed = ", ".join(
        member.value
        for member in enum_class
    )

    raise ValueError(
        f"Invalid {label}. "
        f"Allowed values: {allowed}"
    )


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
        .filter(
            ProjectUser.user_id == user_id
        )
    )

    return query.filter(
        or_(
            Project.created_by == user_id,
            Project.id.in_(
                member_project_ids
            ),
        )
    )


def _apply_date_filters(
    query,
    column,
    created_from,
    created_to,
):
    if created_from is not None:
        query = query.filter(
            column >= created_from
        )

    if created_to is not None:
        query = query.filter(
            column <= created_to
        )

    return query


def _search_projects(
    db,
    user_id,
    role,
    query,
    project_id=None,
    project_status=None,
    created_from=None,
    created_to=None,
):
    project_ids = _accessible_project_ids(
        db,
        user_id,
        role,
    )

    project_query = (
        db.query(Project)
        .filter(
            Project.id.in_(project_ids),
            _text_filter(
                query,
                Project.name,
                Project.description,
            ),
        )
    )

    if project_id is not None:
        project_query = project_query.filter(
            Project.id == project_id
        )

    if project_status is not None:
        clean_status = (
            project_status
            .strip()
            .lower()
        )

        if clean_status not in PROJECT_STATUSES:
            raise ValueError(
                "Invalid project status"
            )

        project_query = project_query.filter(
            func.lower(Project.status)
            == clean_status
        )

    project_query = _apply_date_filters(
        project_query,
        Project.created_at,
        created_from,
        created_to,
    )

    rows = project_query.all()

    return [
        {
            "resource_type": "project",
            "resource_id": row.id,
            "title": row.name,
            "snippet": _snippet(
                row.description
            ),
            "relevance": _score(
                query,
                row.name,
                row.description,
            ),
            "created_at": row.created_at,
            "metadata": {
                "status": row.status,
                "progress": row.progress,
                "company_id": row.company_id,
                "department_id": (
                    row.department_id
                ),
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
    project_id=None,
    task_status=None,
    priority=None,
    created_from=None,
    created_to=None,
):
    project_ids = _accessible_project_ids(
        db,
        user_id,
        role,
    )

    task_query = (
        db.query(Task)
        .filter(
            Task.is_active == True,
            Task.project_id.in_(
                project_ids
            ),
            _text_filter(
                query,
                Task.name,
                Task.description,
            ),
        )
    )

    if project_id is not None:
        task_query = task_query.filter(
            Task.project_id == project_id
        )

    parsed_status = _parse_enum(
        task_status,
        TaskStatusEnum,
        "task status",
    )

    if parsed_status is not None:
        task_query = task_query.filter(
            Task.status == parsed_status
        )

    parsed_priority = _parse_enum(
        priority,
        TaskPriorityEnum,
        "task priority",
    )

    if parsed_priority is not None:
        task_query = task_query.filter(
            Task.priority == parsed_priority
        )

    task_query = _apply_date_filters(
        task_query,
        Task.created_at,
        created_from,
        created_to,
    )

    rows = task_query.all()

    return [
        {
            "resource_type": "task",
            "resource_id": row.id,
            "title": row.name,
            "snippet": _snippet(
                row.description
            ),
            "relevance": _score(
                query,
                row.name,
                row.description,
            ),
            "created_at": row.created_at,
            "metadata": {
                "project_id": row.project_id,
                "team_id": row.team_id,
                "assigned_to": row.assigned_to,
                "status": (
                    row.status.value
                    if hasattr(
                        row.status,
                        "value",
                    )
                    else str(row.status)
                ),
                "priority": (
                    row.priority.value
                    if hasattr(
                        row.priority,
                        "value",
                    )
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
    project_id=None,
    file_type=None,
    created_from=None,
    created_to=None,
):
    normalized_role = _normalize_role(role)

    file_query = db.query(File)

    if project_id is not None:
        file_query = file_query.join(
            Task,
            File.task_id == Task.id,
        )

    file_query = file_query.filter(
        File.is_active == True,
        File.deleted_at.is_(None),
        _text_filter(
            query,
            File.file_name,
        ),
    )

    if project_id is not None:
        project_ids = (
            _accessible_project_ids(
                db,
                user_id,
                role,
            )
        )

        file_query = file_query.filter(
            Task.project_id.in_(
                project_ids
            ),
            Task.project_id == project_id,
        )

    if file_type is not None:
        file_query = file_query.filter(
            func.lower(File.file_type)
            == file_type.strip().lower()
        )

    if normalized_role not in PRIVILEGED_ROLES:
        shared_ids = (
            db.query(FileShare.file_id)
            .filter(
                FileShare.shared_with
                == user_id,
                FileShare.is_active
                == True,
            )
        )

        file_query = file_query.filter(
            or_(
                File.uploaded_by
                == user_id,
                File.id.in_(shared_ids),
            )
        )

    file_query = _apply_date_filters(
        file_query,
        File.created_at,
        created_from,
        created_to,
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
            "created_at": row.created_at,
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
    project_id=None,
    created_from=None,
    created_to=None,
):
    project_ids = _accessible_project_ids(
        db,
        user_id,
        role,
    )

    comment_query = (
        db.query(Comment)
        .join(
            Task,
            Comment.task_id == Task.id,
        )
        .filter(
            Task.is_active == True,
            Task.project_id.in_(
                project_ids
            ),
            _text_filter(
                query,
                Comment.comment,
            ),
        )
    )

    if project_id is not None:
        comment_query = (
            comment_query.filter(
                Task.project_id
                == project_id
            )
        )

    comment_query = _apply_date_filters(
        comment_query,
        Comment.created_at,
        created_from,
        created_to,
    )

    rows = comment_query.all()

    return [
        {
            "resource_type": "comment",
            "resource_id": row.id,
            "title": (
                f"Comment #{row.id}"
            ),
            "snippet": _snippet(
                row.comment
            ),
            "relevance": _score(
                query,
                "",
                row.comment,
            ),
            "created_at": row.created_at,
            "metadata": {
                "task_id": row.task_id,
                "user_id": row.user_id,
            },
        }
        for row in rows
    ]


def _sort_results(results, sort_by):
    if sort_by == "newest":
        results.sort(
            key=lambda item: (
                item["created_at"]
                is not None,
                item["created_at"]
                if item["created_at"]
                is not None
                else datetime.min,
            ),
            reverse=True,
        )

        return

    if sort_by == "oldest":
        results.sort(
            key=lambda item: (
                item["created_at"]
                is None,
                item["created_at"]
                if item["created_at"]
                is not None
                else datetime.max,
            )
        )

        return

    results.sort(
        key=lambda item: (
            item["relevance"],
            item["created_at"]
            is not None,
            item["created_at"]
            if item["created_at"]
            is not None
            else datetime.min,
            item["resource_id"],
        ),
        reverse=True,
    )


def search_all(
    db: Session,
    user_id: int,
    role,
    query: str,
    resource_type: str = "all",
    skip: int = 0,
    limit: int = 20,
    project_id: int | None = None,
    project_status: str | None = None,
    task_status: str | None = None,
    priority: str | None = None,
    file_type: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    min_relevance: float = 0.0,
    sort_by: str = "relevance",
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

    clean_sort = (
        sort_by or "relevance"
    ).strip().lower()

    if clean_sort not in SORT_OPTIONS:
        raise ValueError(
            "Invalid sort option"
        )

    if (
        created_from is not None
        and created_to is not None
        and created_from > created_to
    ):
        raise ValueError(
            "created_from cannot be "
            "after created_to"
        )

    if min_relevance < 0 or min_relevance > 1:
        raise ValueError(
            "min_relevance must be "
            "between 0 and 1"
        )

    results = []

    if clean_type in {"all", "project"}:
        results.extend(
            _search_projects(
                db,
                user_id,
                role,
                clean_query,
                project_id,
                project_status,
                created_from,
                created_to,
            )
        )

    if clean_type in {"all", "task"}:
        results.extend(
            _search_tasks(
                db,
                user_id,
                role,
                clean_query,
                project_id,
                task_status,
                priority,
                created_from,
                created_to,
            )
        )

    if clean_type in {"all", "file"}:
        results.extend(
            _search_files(
                db,
                user_id,
                role,
                clean_query,
                project_id,
                file_type,
                created_from,
                created_to,
            )
        )

    if clean_type in {"all", "comment"}:
        results.extend(
            _search_comments(
                db,
                user_id,
                role,
                clean_query,
                project_id,
                created_from,
                created_to,
            )
        )

    results = [
        item
        for item in results
        if item["relevance"]
        >= min_relevance
    ]

    _sort_results(
        results,
        clean_sort,
    )

    total = len(results)

    filters = {
        "project_id": project_id,
        "project_status": project_status,
        "task_status": task_status,
        "priority": priority,
        "file_type": file_type,
        "created_from": created_from,
        "created_to": created_to,
        "min_relevance": min_relevance,
    }

    return {
        "query": clean_query,
        "resource_type": clean_type,
        "total": total,
        "skip": skip,
        "limit": limit,
        "sort_by": clean_sort,
        "filters": filters,
        "results": results[
            skip:skip + limit
        ],
    }
