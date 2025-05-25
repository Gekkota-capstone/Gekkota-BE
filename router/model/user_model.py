# /router/model/user_model.py

from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50)
    profile: Optional[str] = None


class UserCreate(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50)
    profile: Optional[str] = None


class UserUpdate(BaseModel):
    profile: Optional[str] = None


class UserResponse(UserBase):
    class Config:
        from_attributes = True