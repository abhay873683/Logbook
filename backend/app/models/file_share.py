from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class FileShare(Base):
    __tablename__ = "file_shares"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_id = Column(
        Integer,
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False
    )

    shared_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    shared_with = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    permission = Column(
        String(10),
        nullable=False,
        default="read"
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # ---------------------------------
    # Relationships
    # ---------------------------------

    file = relationship(
        "File",
        backref="shares"
    )

    sharer = relationship(
        "User",
        foreign_keys=[shared_by]
    )

    receiver = relationship(
        "User",
        foreign_keys=[shared_with]
    )

    def __repr__(self):
        return f"<FileShare file_id={self.file_id}>"