from typing import Optional

from pydantic import BaseModel, EmailStr


# -------------------------
# Create User Schema
# -------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "user"
    is_active: bool = True


# -------------------------
# Update User Schema
# -------------------------
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# -------------------------
# Login Response Token
# -------------------------
class Token(BaseModel):
    access_token: str
    token_type: str


# -------------------------
# User Response Schema
# -------------------------
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# -------------------------
# Change Password Schema
# -------------------------
class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str