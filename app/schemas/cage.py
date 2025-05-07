from pydantic import BaseModel
from typing import Optional, List

# 케이지 기본 스키마
class CageBase(BaseModel):
    name: str  # 케이지 이름
    species: str  # 파충류 종류
    gender: str  # 파충류 성별
    birth_date: str  # 파충류 생일
    cleaning_cycle: Optional[int] = -1  # 청소 주기 (일 단위, 기본값: -1)

    model_config = {
        "from_attributes": True
    }

# 케이지 생성 요청 스키마
class CageCreate(CageBase):
    pass

# 케이지 정보 업데이트 요청 스키마
class CageUpdate(BaseModel):
    name: Optional[str] = None  # 변경할 케이지 이름
    species: Optional[str] = None  # 변경할 파충류 종류
    gender: Optional[str] = None  # 변경할 파충류 성별
    birth_date: Optional[str] = None  # 변경할 파충류 생일
    cleaning_cycle: Optional[int] = None  # 변경할 청소 주기
    state: Optional[str] = None  # 변경할 케이지 상태

    model_config = {
        "from_attributes": True
    }

# 케이지 상태 응답 스키마
class CageStateResponse(BaseModel):
    state: str

    model_config = {
        "from_attributes": True
    }

# 케이지 정보 응답 스키마
class CageOut(CageBase):
    id: int  # 케이지 ID
    state: Optional[str] = None  # 케이지 상태

    model_config = {
        "from_attributes": True
    }

# 케이지 목록 응답 스키마
class CageListResponse(BaseModel):
    list: List[CageOut]

    model_config = {
        "from_attributes": True
    }