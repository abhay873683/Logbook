from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class FileVersion(Base):
    __tablename__ = "file_versions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    file_id = Column(
        Integer,
        ForeignKey(
            "files.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    version_number = Column(
        Integer,
        nullable=False,
    )

    file_path = Column(
        String(500),
        nullable=False,
    )

    file_size = Column(
        Integer,
        nullable=True,
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    file = relationship(
        "File",
        back_populates="versions",
    )

    uploader = relationship(
        "User",
        foreign_keys=[uploaded_by],
    )

    __table_args__ = (
        UniqueConstraint(
            "file_id",
            "version_number",
            name="uq_file_version_number",
        ),
    )