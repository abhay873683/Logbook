from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class DashboardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    layout: Optional[dict[str, Any]] = None


class DashboardUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: Optional[str] = None
    layout: Optional[dict[str, Any]] = None


class DashboardLayoutUpdate(BaseModel):
    layout: dict[str, Any]


class DashboardResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    layout: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WidgetCreate(BaseModel):
    dashboard_id: int
    title: str = Field(min_length=1, max_length=255)
    widget_type: str
    config: Optional[dict[str, Any]] = None
    size_x: int = Field(default=2, ge=1)
    size_y: int = Field(default=2, ge=1)
    position_x: int = Field(default=0, ge=0)
    position_y: int = Field(default=0, ge=0)


class WidgetUpdate(BaseModel):
    title: Optional[str] = None
    widget_type: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    size_x: Optional[int] = Field(default=None, ge=1)
    size_y: Optional[int] = Field(default=None, ge=1)
    position_x: Optional[int] = Field(default=None, ge=0)
    position_y: Optional[int] = Field(default=None, ge=0)


class WidgetResponse(BaseModel):
    id: int
    dashboard_id: int
    user_id: int
    title: str
    widget_type: str
    config: Optional[dict[str, Any]] = None
    size_x: int
    size_y: int
    position_x: int
    position_y: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)