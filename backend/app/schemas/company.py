from typing import Optional

from pydantic import BaseModel, EmailStr


# -------------------------
# Create Company
# -------------------------
class CompanyCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True


# -------------------------
# Update Company
# -------------------------
class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


# -------------------------
# Company Response
# -------------------------
class CompanyResponse(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr]
    phone: Optional[str]
    address: Optional[str]
    website: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True