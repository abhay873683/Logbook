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


# -----------------------------
# Task Model
# -----------------------------
class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        Enum(TaskStatusEnum),
        default=TaskStatusEnum.todo
    )

    priority = Column(
        Enum(TaskPriorityEnum),
        default=TaskPriorityEnum.medium
    )

    start_date = Column(
        DateTime(timezone=True),
        nullable=True
    )

    due_date = Column(
        DateTime(timezone=True),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # ----------------------------------
    # Relationships
    # ----------------------------------

    project = relationship(
        "Project",
        back_populates="tasks"
    )

    assigned_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_tasks"
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_tasks"
    )

    subtasks = relationship(
        "Subtask",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    comments = relationship(
        "Comment",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    files = relationship(
        "File",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    # ----------------------------------
    # Day 20 - Progress History
    # ----------------------------------

    progress_history = relationship(
        "TaskProgress",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    # ----------------------------------
    # TreeFlow - Task Dependencies
    # ----------------------------------

    # Tasks that depend on this task
    #
    # Example:
    # Task A -> Task B
    #
    # For Task A:
    # dependencies_before = [Task B dependency]

    dependencies_before = relationship(
        "Dependency",
        foreign_keys="Dependency.predecessor_task_id",
        back_populates="predecessor",
        cascade="all, delete-orphan"
    )

    # Tasks that this task depends on
    #
    # Example:
    # Task A -> Task B
    #
    # For Task B:
    # dependencies_after = [Task A dependency]

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
        return f"<Task {self.name}>"