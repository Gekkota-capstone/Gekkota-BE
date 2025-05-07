from pydantic import BaseModel
from datetime import date
from typing import List

# 카메라 데이터 응답 스키마
class CameraDataOut(BaseModel):
    id: int  # 카메라 데이터 ID
    cage_id: int  # 케이지 ID
    record_date: date  # 녹화 날짜
    video_url: List[str]  # 비디오 URL 목록

    model_config = {
        "from_attributes": True
    }