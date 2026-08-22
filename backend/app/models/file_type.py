from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)
from sqlalchemy.sql import func

from app.core.database import Base


class FileType(Base):
    __tablename__ = "file_types"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    extension = Column(
        String(20),
        nullable=False,
        unique=True
    )

    mime_type = Column(
        String(150),
        nullable=True
    )

    icon = Column(
        String(50),
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

    def __repr__(self):
        return f"<FileType {self.name}>"