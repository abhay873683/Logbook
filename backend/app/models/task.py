from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

import enum


# -----------------------------
# Task Status Enum
# -----------------------------
class TaskStatusEnum(str, enum.Enum):
    todo = "To Do"
    in_progress = "In Progress"
    review = "Review"
    done = "Done"
    cancelled = "Cancelled"


# -----------------------------
# Task Priority Enum
# -----------------------------
class TaskPriorityEnum(str, enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


# -----------------------------
# Task Model
# -----------------------------
class Task(Base):
    __tablename__ = "tasks"

    # ----------------------------------
    # Primary Key
    # ----------------------------------
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ----------------------------------
    # Task Name
    # ----------------------------------
    name = Column(
        String(255),
        nullable=False
    )

    # ----------------------------------
    # Description
    # ----------------------------------
    description = Column(
        Text,
        nullable=True
    )

    # ----------------------------------
    # Project
    # ----------------------------------
    project_id = Column(
        Integer,
        ForeignKey(
            "projects.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # ----------------------------------
    # Team - Day 29
    # ----------------------------------
    team_id = Column(
        Integer,
        ForeignKey(
            "teams.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    # ----------------------------------
    # Legacy Single Assigned User
    # ----------------------------------
    assigned_to = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    # ----------------------------------
    # Created By
    # ----------------------------------
    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # ----------------------------------
    # Status
    # ----------------------------------
    status = Column(
        Enum(TaskStatusEnum),
        default=TaskStatusEnum.todo,
        nullable=False
    )

    # ----------------------------------
    # Priority
    # ----------------------------------
    priority = Column(
        Enum(TaskPriorityEnum),
        default=TaskPriorityEnum.medium,
        nullable=False
    )

    # ----------------------------------
    # Dates
    # ----------------------------------
    start_date = Column(
        DateTime(timezone=True),
        nullable=True
    )

    due_date = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # ----------------------------------
    # Progress - Day 29
    # ----------------------------------
    progress = Column(
        Integer,
        default=0,
        nullable=False
    )

    # ----------------------------------
    # Active Status
    # ----------------------------------
    is_active = Column(
        Boolean,
        default=True
    )

    # ----------------------------------
    # Created At
    # ----------------------------------
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # ----------------------------------
    # Updated At
    # ----------------------------------
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # ==================================================
    # Relationships
    # ==================================================

    # ----------------------------------
    # Project
    # ----------------------------------
    project = relationship(
        "Project",
        back_populates="tasks"
    )

    # ----------------------------------
    # Team
    # ----------------------------------
    team = relationship(
        "Team",
        back_populates="tasks"
    )

    # ----------------------------------
    # Legacy Single Assigned User
    # ----------------------------------
    assigned_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_tasks"
    )

    # ----------------------------------
    # Creator
    # ----------------------------------
    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_tasks"
    )

    # ----------------------------------
    # Multiple Assignees - Day 29
    # ----------------------------------
    task_assignees = relationship(
        "TaskAssignee",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    # ----------------------------------
    # Subtasks
    # ----------------------------------
    subtasks = relationship(
        "Subtask",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    # ----------------------------------
    # Comments
    # ----------------------------------
    comments = relationship(
        "Comment",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    # ----------------------------------
    # Files
    # ----------------------------------
    files = relationship(
        "File",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    # ----------------------------------
    # Progress History
    # ----------------------------------
    progress_history = relationship(
        "TaskProgress",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    # ----------------------------------
    # Dependencies Before
    # ----------------------------------
    dependencies_before = relationship(
        "Dependency",
        foreign_keys="Dependency.predecessor_task_id",
        back_populates="predecessor",
        cascade="all, delete-orphan"
    )

    # ----------------------------------
    # Dependencies After
    # ----------------------------------
    dependencies_after = relationship(
        "Dependency",
        foreign_keys="Dependency.successor_task_id",
        back_populates="successor",
        cascade="all, delete-orphan"
    )

    # ----------------------------------
    # Representation
    # ----------------------------------
    def __repr__(self):
        return (
            f"<Task(id={self.id}, "
            f"name='{self.name}', "
            f"project_id={self.project_id}, "
            f"team_id={self.team_id})>"
        )