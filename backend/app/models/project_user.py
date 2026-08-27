from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProjectUser(Base):
    __tablename__ = "project_users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(
        String(50),
        nullable=False,
        default="member",
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "user_id",
            name="uq_project_user",
        ),
    )

    project = relationship(
        "Project",
        foreign_keys=[project_id],
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
    )

    def __repr__(self):
        return (
            f"<ProjectUser("
            f"id={self.id}, "
            f"project_id={self.project_id}, "
            f"user_id={self.user_id}, "
            f"role='{self.role}'"
            f")>"
        )