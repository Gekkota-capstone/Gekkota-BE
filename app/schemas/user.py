from pydantic import BaseModel, validator
from typing import Optional

# 사용자 생성 요청 스키마
class UserCreate(BaseModel):
    google_token: str  # Google OAuth 토큰

# 사용자 정보 업데이트 요청 스키마
class UserUpdate(BaseModel):
    nickname: str  # 변경할 닉네임
    
    # 닉네임 유효성 검사
    @validator('nickname')
    def validate_nickname(cls, v):
        if len(v) < 1:
            raise ValueError('닉네임은 최소 1자 이상이어야 합니다')
        return v

# 사용자 정보 응답 스키마
class UserOut(BaseModel):
    id: int  # 사용자 ID
    nickname: Optional[str]  # 사용자 닉네임 (선택적)

    class Config:
        orm_mode = True  # ORM 모델과의 호환성 설정