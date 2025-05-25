# /router/model/pet_feed_model.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PetFeedBase(BaseModel):
    food_type: Optional[str] = Field(None, min_length=1)  # null 응답을 위해 Optional로 변경
    food_size: Optional[str] = None
    food_amount: Optional[float] = None
    amount_unit: Optional[str] = None
    memo: Optional[str] = None  # message -> memo 변경


class PetFeedCreate(BaseModel):  # PetFeedBase 상속 제거하고 직접 정의
    date: date
    food_type: str = Field(..., min_length=1)  # 생성 시에는 필수
    food_size: Optional[str] = None
    food_amount: Optional[float] = None
    amount_unit: Optional[str] = None
    memo: Optional[str] = None


class PetFeedUpdate(BaseModel):
    food_type: Optional[str] = Field(None, min_length=1)
    food_size: Optional[str] = None
    food_amount: Optional[float] = None
    amount_unit: Optional[str] = None
    memo: Optional[str] = None  # message -> memo 변경


class PetFeedResponse(PetFeedBase):
    pet_id: str
    date: date

    class Config:
        from_attributes = True