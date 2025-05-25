# /router/model/pet_model.py (기존 파일에 PetUpdate 추가)

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PetBase(BaseModel):
    name: str = Field(..., min_length=1)
    gender: str = Field(..., min_length=1)
    species: str = Field(..., min_length=1)
    birthdate: Optional[date] = None


class PetCreate(PetBase):
    pass


class PetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    gender: Optional[str] = Field(None, min_length=1)
    species: Optional[str] = Field(None, min_length=1)
    birthdate: Optional[date] = None


class PetResponse(PetBase):
    pet_id: str

    class Config:
        from_attributes = True