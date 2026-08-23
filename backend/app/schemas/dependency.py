from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ----------------------------------
# Dependency Base Schema
# ----------------------------------

class DependencyBase(BaseModel):
    predecessor_task_id: int = Field(
        ...,
        gt=0,
        description="ID of the task that must be completed first"
    )

    successor_task_id: int = Field(
        ...,
        gt=0,
        description="ID of the task that depends on the predecessor"
    )

    dependency_type: str = Field(
        default="finish_to_start",
        min_length=1,
        max_length=50,
        description="Type of dependency between two tasks"
    )

    lag_days: int = Field(
        default=0,
        ge=0,
        description="Number of buffer/delay days"
    )


# ----------------------------------
# Create Dependency Schema
# ----------------------------------

class DependencyCreate(DependencyBase):
    pass


# ----------------------------------
# Update Dependency Schema
# ----------------------------------

class DependencyUpdate(BaseModel):
    dependency_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    lag_days: int | None = Field(
        default=None,
        ge=0
    )


# ----------------------------------
# Dependency Response Schema
# ----------------------------------

class DependencyResponse(DependencyBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )