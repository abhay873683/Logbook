from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TeamBase(BaseModel):
    name: str
    description: str | None = None
    department_id: int
    team_lead_id: int | None = None
    is_active: bool = True


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    department_id: int | None = None
    team_lead_id: int | None = None
    is_active: bool | None = None


class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)