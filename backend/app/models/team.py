from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Team(Base):
    __tablename__ = "teams"

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

    department_id = Column(
        Integer,
        ForeignKey(
            "departments.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    team_lead_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
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

    # ---------------------------------
    # Relationships
    # ---------------------------------

    department = relationship(
        "Department",
        back_populates="teams"
    )

    team_lead = relationship(
        "User",
        foreign_keys=[team_lead_id],
        back_populates="teams_led"
    )

    # Day 28 - Team -> Projects
    projects = relationship(
        "Project",
        back_populates="team"
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            "department_id",
            name="uq_team_name_department"
        ),
    )

    def __repr__(self):
        return (
            f"<Team(id={self.id}, "
            f"name='{self.name}', "
            f"department_id={self.department_id})>"
        )