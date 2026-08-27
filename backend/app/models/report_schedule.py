from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ReportSchedule(Base):
    __tablename__ = "report_schedules"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    report_id = Column(
        Integer,
        ForeignKey(
            "reports.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    frequency = Column(
        String(50),
        nullable=False,
    )

    recipients = Column(
        JSON,
        nullable=True,
    )

    next_run = Column(
        DateTime(timezone=True),
        nullable=True,
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

    report = relationship(
        "Report",
        back_populates="schedules",
    )

    def __repr__(self):
        return (
            f"<ReportSchedule id={self.id} "
            f"report_id={self.report_id} "
            f"frequency={self.frequency}>"
        )