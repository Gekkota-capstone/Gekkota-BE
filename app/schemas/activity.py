from pydantic import BaseModel
from datetime import date, datetime

# 활동량 데이터 응답 스키마
class ActivityDataOut(BaseModel):
    timestamp: datetime  # 활동량 측정 시간
    activity_level: float  # 활동량 수준 (0.0 ~ 1.0)

    class Config:
        orm_mode = True  # ORM 모델과의 호환성 설정