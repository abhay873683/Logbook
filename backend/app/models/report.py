from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    report_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    filters = Column(
        JSON,
        nullable=True,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    schedules = relationship(
        "ReportSchedule",
        back_populates="report",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Report id={self.id} "
            f"name={self.name} "
            f"type={self.report_type}>"
        )