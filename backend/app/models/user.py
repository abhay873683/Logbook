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

    # ---------------------------------
    # Primary Key
    # ---------------------------------
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ---------------------------------
    # Name
    # ---------------------------------
    name = Column(
        String(255),
        nullable=False
    )

    # ---------------------------------
    # Email
    # ---------------------------------
    email = Column(
        String(255),
        unique=True,
        nullable=False
    )

    # ---------------------------------
    # Password
    # ---------------------------------
    password = Column(
        String(255),
        nullable=False
    )

    # ---------------------------------
    # Role
    # ---------------------------------
    role = Column(
        String(50),
        default="user"
    )

    # ---------------------------------
    # Status
    # ---------------------------------
    is_active = Column(
        Boolean,
        default=True
    )

    # ---------------------------------
    # Created At
    # ---------------------------------
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # ---------------------------------
    # Updated At
    # ---------------------------------
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
    # Subtask Progress Updates
    # ---------------------------------
    subtask_progress = relationship(
        "SubtaskProgress",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ---------------------------------
    # Comment Replies
    # ---------------------------------
    comment_replies = relationship(
        "CommentReply",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ---------------------------------
    # Activity Logs
    # ---------------------------------
    activity_logs = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ---------------------------------
    # Teams Led
    # ---------------------------------
    teams_led = relationship(
        "Team",
        foreign_keys="Team.team_lead_id",
        back_populates="team_lead"
    )

    # ---------------------------------
    # Object Representation
    # ---------------------------------
    def __repr__(self):
        return f"<User {self.email}>"