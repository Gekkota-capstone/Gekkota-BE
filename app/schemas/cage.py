from pydantic import BaseModel
from datetime import date
from typing import Optional

# 케이지 기본 스키마
class CageBase(BaseModel):
    name: str  # 케이지 이름
    species: str  # 파충류 종류
    gender: str  # 파충류 성별
    birth_date: date  # 파충류 생일
    cleaning_cycle: Optional[int] = -1  # 청소 주기 (일 단위, 기본값: -1)

# 케이지 생성 요청 스키마
class CageCreate(CageBase):
    pass

# 케이지 정보 업데이트 요청 스키마
class CageUpdate(BaseModel):
    name: Optional[str] = None  # 변경할 케이지 이름
    species: Optional[str] = None  # 변경할 파충류 종류
    gender: Optional[str] = None  # 변경할 파충류 성별
    birth_date: Optional[date] = None  # 변경할 파충류 생일
    cleaning_cycle: Optional[int] = None  # 변경할 청소 주기

# 케이지 정보 응답 스키마
class CageOut(CageBase):
    id: int  # 케이지 ID

    class Config:
        orm_mode = True  # ORM 모델과의 호환성 설정