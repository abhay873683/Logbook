from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ----------------------------------------
# Base Schema
# ----------------------------------------
class ProjectBase(BaseModel):
    name: str

    description: str | None = None

    company_id: int

    department_id: int | None = None

    team_id: int | None = None

    start_date: datetime | None = None

    end_date: datetime | None = None

    status: str = "Planned"

    progress: int = Field(
        default=0,
        ge=0,
        le=100,
    )

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
    name: str | None = None

    description: str | None = None

    company_id: int | None = None

    department_id: int | None = None

    team_id: int | None = None

    start_date: datetime | None = None

    end_date: datetime | None = None

    status: str | None = None

    progress: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    is_active: bool | None = None


# ----------------------------------------
# Response Schema
# ----------------------------------------
class ProjectResponse(BaseModel):
    id: int

    name: str

    description: str | None

    company_id: int

    department_id: int | None

    team_id: int | None

    created_by: int

    start_date: datetime | None

    end_date: datetime | None

    status: str

    progress: int

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )