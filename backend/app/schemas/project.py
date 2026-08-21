from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr


# ----------------------------------------
# Base Schema
# ----------------------------------------
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    company_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "Planned"
    is_active: bool = True


# ----------------------------------------
# Create Project
# ----------------------------------------
class ProjectCreate(ProjectBase):
    pass


# ----------------------------------------
# Update Project
# ----------------------------------------
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    company_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


# ----------------------------------------
# Response Schema
# ----------------------------------------
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    company_id: int
    created_by: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True