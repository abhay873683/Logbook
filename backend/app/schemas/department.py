from typing import Optional

from pydantic import BaseModel


# -------------------------
# Create Department
# -------------------------
class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    company_id: int
    is_active: bool = True


# -------------------------
# Update Department
# -------------------------
class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    company_id: Optional[int] = None
    is_active: Optional[bool] = None


# -------------------------
# Department Response
# -------------------------
class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    company_id: int
    is_active: bool

    class Config:
        from_attributes = True