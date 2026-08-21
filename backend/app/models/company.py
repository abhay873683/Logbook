from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(255),
        unique=True,
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=True
    )

    phone = Column(
        String(20),
        nullable=True
    )

    address = Column(
        String(500),
        nullable=True
    )

    website = Column(
        String(255),
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

    # Relationships
    departments = relationship(
        "Department",
        back_populates="company",
        cascade="all, delete"
    )

    projects = relationship(
        "Project",
        back_populates="company",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Company {self.name}>"