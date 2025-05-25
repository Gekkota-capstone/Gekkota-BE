# /router/model/pet_active_model.py

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TimeActivity(BaseModel):
    hour: int
    value: float

class DayActivity(BaseModel):
    day: str
    value: float

class MostActiveTime(BaseModel):
    start: int
    end: int

class PetActiveResponse(BaseModel):
    pet_id: str
    abnormalBehavior: str
    highlightVideoUrl: List[str] = []  # 배열로 변경
    mostActive: MostActiveTime  # 새로운 필드
    heatmapImageUrl: Optional[str] = None
    timeOfActivity: List[TimeActivity]
    recentDatOfActivity: List[DayActivity]