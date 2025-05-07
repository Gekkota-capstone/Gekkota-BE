from pydantic import BaseModel
from datetime import date
from typing import Optional, List

# 건강 기록 생성 요청 스키마
class HealthCreate(BaseModel):
    cage_id: int  # 건강 기록할 케이지 ID
    record_date: date  # 기록 날짜
    weight: float  # 체중 (g)
    memo: Optional[str] = None  # 메모
    shedding_status: Optional[str] = None  # 탈피 상태
    photo_urls: List[str] = []  # 건강 상태 사진 URL 목록

    model_config = {
        "from_attributes": True
    }

# 건강 기록 응답 스키마
class HealthOut(HealthCreate):
    id: int  # 건강 기록 ID
    photo_urls: Optional[List[str]] = []  # 건강 상태 사진 URL 목록 (선택적)

    model_config = {
        "from_attributes": True
    }