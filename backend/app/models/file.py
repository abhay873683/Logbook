from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    task_id = Column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )

    folder_id = Column(
        Integer,
        ForeignKey("folders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    file_name = Column(
        String(255),
        nullable=False,
    )

    file_path = Column(
        String(500),
        nullable=False,
    )

    file_type = Column(
        String(100),
        nullable=True,
    )

    file_size = Column(
        Integer,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    is_downloadable = Column(
        Boolean,
        default=True,
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    deleted_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    task = relationship(
        "Task",
        back_populates="files",
    )

    folder = relationship(
        "Folder",
        back_populates="files",
    )

    uploader = relationship(
        "User",
        back_populates="uploaded_files",
        foreign_keys=[uploaded_by],
    )

    versions = relationship(
        "FileVersion",
        back_populates="file",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<File("
            f"id={self.id}, "
            f"file_name='{self.file_name}', "
            f"task_id={self.task_id}, "
            f"folder_id={self.folder_id})>"
        )
