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


class Department(Base):
    __tablename__ = "departments"

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
        String(500),
        nullable=True
    )

    company_id = Column(
        Integer,
        ForeignKey(
            "companies.id",
            ondelete="CASCADE"
        ),
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
        back_populates="departments"
    )

    teams = relationship(
        "Team",
        back_populates="department",
        cascade="all, delete-orphan"
    )

    # Day 28 - Department -> Projects
    projects = relationship(
        "Project",
        back_populates="department"
    )

    # Future Employee Module
    # employees = relationship(
    #     "Employee",
    #     back_populates="department",
    #     cascade="all, delete-orphan"
    # )

    def __repr__(self):
        return (
            f"<Department(id={self.id}, "
            f"name='{self.name}', "
            f"company_id={self.company_id})>"
        )