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

    # ---------------------------------
    # Company
    # ---------------------------------
    company_id = Column(
        Integer,
        ForeignKey(
            "companies.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # ---------------------------------
    # Department - Day 28
    # ---------------------------------
    department_id = Column(
        Integer,
        ForeignKey(
            "departments.id",
            ondelete="CASCADE"
        ),
        nullable=True
    )

    # ---------------------------------
    # Team - Day 28
    # ---------------------------------
    team_id = Column(
        Integer,
        ForeignKey(
            "teams.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    # ---------------------------------
    # Creator
    # ---------------------------------
    created_by = Column(
        Integer,
        ForeignKey(
            "users.id"
        ),
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
        default="Planned"
    )

    # ---------------------------------
    # Project Progress - Day 28
    # 0 to 100
    # ---------------------------------
    progress = Column(
        Integer,
        default=0,
        nullable=False
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

    company = relationship(
        "Company",
        back_populates="projects"
    )

    department = relationship(
        "Department",
        back_populates="projects"
    )

    team = relationship(
        "Team",
        back_populates="projects"
    )

    creator = relationship(
        "User",
        back_populates="projects_created",
        foreign_keys=[created_by]
    )

    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Project(id={self.id}, "
            f"name='{self.name}', "
            f"company_id={self.company_id}, "
            f"department_id={self.department_id}, "
            f"team_id={self.team_id})>"
        )