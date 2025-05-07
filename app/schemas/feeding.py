from pydantic import BaseModel
from datetime import date

# 급여 기록 생성 요청 스키마
class FeedingCreate(BaseModel):
    cage_id: int  # 급여할 케이지 ID
    feeding_date: date  # 급여 날짜
    food_type: str  # 사료 종류
    food_size: str  # 사료 크기
    food_amount: int  # 급여량

    model_config = {
        "from_attributes": True
    }

# 급여 기록 응답 스키마
class FeedingOut(FeedingCreate):
    id: int  # 급여 기록 ID

    model_config = {
        "from_attributes": True
    }