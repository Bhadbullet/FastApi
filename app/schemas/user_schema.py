import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user_model import UserRole


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class AdminCreateUser(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    profile_image: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True