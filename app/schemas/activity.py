from pydantic import BaseModel
from datetime import datetime

# 활동량 데이터 응답 스키마
class ActivityDataOut(BaseModel):
    timestamp: datetime  # 활동량 측정 시간
    activity_level: float  # 활동량 수준 (0.0 ~ 1.0)

    model_config = {
        "from_attributes": True
    }