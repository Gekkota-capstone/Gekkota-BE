from pydantic import BaseModel
from datetime import date

# 청소 기록 생성 요청 스키마
class CleaningCreate(BaseModel):
    cage_id: int  # 청소할 케이지 ID
    cleaning_date: date  # 청소 날짜

# 청소 기록 응답 스키마
class CleaningOut(CleaningCreate):
    id: int  # 청소 기록 ID

    class Config:
        orm_mode = True  # ORM 모델과의 호환성 설정

# 청소 주기 업데이트 요청 스키마
class CleaningCycleUpdate(BaseModel):
    cleaning_cycle: int  # 변경할 청소 주기 (일 단위)