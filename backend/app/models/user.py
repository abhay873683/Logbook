from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        default="user"
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

    # ---------------------------------
    # Projects Created
    # ---------------------------------

    projects_created = relationship(
        "Project",
        back_populates="creator",
        foreign_keys="Project.created_by"
    )

    # ---------------------------------
    # Tasks Assigned
    # ---------------------------------

    assigned_tasks = relationship(
        "Task",
        foreign_keys="Task.assigned_to",
        back_populates="assigned_user"
    )

    # ---------------------------------
    # Tasks Created
    # ---------------------------------

    created_tasks = relationship(
        "Task",
        foreign_keys="Task.created_by",
        back_populates="creator"
    )

    # ---------------------------------
    # Subtasks Assigned
    # ---------------------------------

    assigned_subtasks = relationship(
        "Subtask",
        foreign_keys="Subtask.assigned_to",
        back_populates="assigned_user"
    )

    # ---------------------------------
    # Subtasks Created
    # ---------------------------------

    created_subtasks = relationship(
        "Subtask",
        foreign_keys="Subtask.created_by",
        back_populates="creator"
    )

    # ---------------------------------
    # Comments
    # ---------------------------------

    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ---------------------------------
    # Uploaded Files
    # ---------------------------------

    uploaded_files = relationship(
        "File",
        back_populates="uploader",
        foreign_keys="File.uploaded_by",
        cascade="all, delete-orphan"
    )

    # ---------------------------------
    # Task Progress Updates
    # ---------------------------------

    progress_updates = relationship(
        "TaskProgress",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ---------------------------------
    # Notifications
    # ---------------------------------

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ---------------------------------
    # Subtask Progress Updates (Day 21)
    # ---------------------------------

    subtask_progress = relationship(
        "SubtaskProgress",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ---------------------------------
    # Comment Replies (Day 21)
    # ---------------------------------

    comment_replies = relationship(
        "CommentReply",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ---------------------------------
    # Activity Logs (Day 21)
    # ---------------------------------

    activity_logs = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"