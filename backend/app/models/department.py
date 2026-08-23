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

    # -------------------------
    # Primary Key
    # -------------------------
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # -------------------------
    # Department Name
    # -------------------------
    name = Column(
        String(255),
        nullable=False
    )

    # -------------------------
    # Department Description
    # -------------------------
    description = Column(
        String(500),
        nullable=True
    )

    # -------------------------
    # Company Foreign Key
    # -------------------------
    company_id = Column(
        Integer,
        ForeignKey(
            "companies.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # -------------------------
    # Status
    # -------------------------
    is_active = Column(
        Boolean,
        default=True
    )

    # -------------------------
    # Created At
    # -------------------------
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # -------------------------
    # Updated At
    # -------------------------
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # -------------------------
    # Relationship with Company
    # -------------------------
    company = relationship(
        "Company",
        back_populates="departments"
    )

    # -------------------------
    # Department -> Teams
    # -------------------------
    teams = relationship(
        "Team",
        back_populates="department",
        cascade="all, delete-orphan"
    )

    # ----------------------------------------------------
    # Employee Relationship
    # Future Employee Module
    # ----------------------------------------------------

    # employees = relationship(
    #     "Employee",
    #     back_populates="department",
    #     cascade="all, delete-orphan"
    # )

    # -------------------------
    # Object Representation
    # -------------------------
    def __repr__(self):
        return (
            f"<Department(id={self.id}, "
            f"name='{self.name}', "
            f"company_id={self.company_id})>"
        )