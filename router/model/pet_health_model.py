# /router/model/pet_health_model.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import date


class WeightDataPoint(BaseModel):
    day: Optional[str] = None
    month: Optional[str] = None
    value: Optional[float] = None


class PetHealthBase(BaseModel):
    weight: Optional[float] = None
    memo: Optional[str] = None
    shedding_status: Optional[str] = None


class PetHealthCreate(PetHealthBase):
    date: date


class PetHealthUpdate(BaseModel):
    weight: Optional[float] = None
    memo: Optional[str] = None
    shedding_status: Optional[str] = None


# 별도의 클래스 대신 Dict[str, Any]로 처리
class PetHealthResponse(PetHealthBase):
    pet_id: str
    date: date
    monthOfWeight: List[Dict[str, Any]] = []
    yearOfWeight: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True