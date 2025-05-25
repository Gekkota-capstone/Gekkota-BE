# /router/model/pet_clean_model.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PetCleanBase(BaseModel):
    memo: Optional[str] = None


class PetCleanCreate(PetCleanBase):
    date: date


class PetCleanUpdate(PetCleanBase):
    pass


class PetCleanResponse(PetCleanBase):
    pet_id: str
    date: date

    class Config:
        from_attributes = True  # 이전의 orm_mode=True와 동일