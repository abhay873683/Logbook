from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class File(Base):
    __tablename__ = "files"

    # ---------------------------------
    # Primary Key
    # ---------------------------------
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ---------------------------------
    # Task
    # ---------------------------------
    task_id = Column(
        Integer,
        ForeignKey(
            "tasks.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # ---------------------------------
    # Uploaded By
    # ---------------------------------
    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # ---------------------------------
    # File Name
    # ---------------------------------
    file_name = Column(
        String(255),
        nullable=False
    )

    # ---------------------------------
    # File Path
    # ---------------------------------
    file_path = Column(
        String(500),
        nullable=False
    )

    # ---------------------------------
    # File Type
    # ---------------------------------
    file_type = Column(
        String(100),
        nullable=True
    )

    # ---------------------------------
    # File Size
    # ---------------------------------
    file_size = Column(
        Integer,
        nullable=True
    )

    # ---------------------------------
    # Active Status
    # ---------------------------------
    is_active = Column(
        Boolean,
        default=True
    )

    # ---------------------------------
    # Download Permission
    # ---------------------------------
    is_downloadable = Column(
        Boolean,
        default=True
    )

    # ---------------------------------
    # Soft Delete Information
    # ---------------------------------
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    deleted_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # ---------------------------------
    # Created At
    # ---------------------------------
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # =================================================
    # Relationships
    # =================================================

    task = relationship(
        "Task",
        back_populates="files"
    )

    uploader = relationship(
        "User",
        back_populates="uploaded_files",
        foreign_keys=[uploaded_by]
    )

    # ---------------------------------
    # File Versions - Day 32
    # ---------------------------------
    versions = relationship(
        "FileVersion",
        back_populates="file",
        cascade="all, delete-orphan"
    )

    # ---------------------------------
    # Representation
    # ---------------------------------
    def __repr__(self):
        return (
            f"<File("
            f"id={self.id}, "
            f"file_name='{self.file_name}', "
            f"task_id={self.task_id})>"
        )