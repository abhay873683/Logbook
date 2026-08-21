from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    start_date = Column(
        DateTime(timezone=True),
        nullable=True
    )

    end_date = Column(
        DateTime(timezone=True),
        nullable=True
    )

    status = Column(
        String(50),
        default="Planning"
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
    # Relationships
    # ---------------------------------

    # Company -> Projects
    company = relationship(
        "Company",
        back_populates="projects"
    )

    # User -> Created Projects
    creator = relationship(
        "User",
        back_populates="projects_created",
        foreign_keys=[created_by]
    )

    # Project -> Tasks
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project {self.name}>"