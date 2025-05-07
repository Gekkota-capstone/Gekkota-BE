from pydantic import BaseModel
from typing import Optional

# 프로필 등록 요청 스키마
class ProfileCreate(BaseModel):
    nickname: str
    profile: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

# 프로필 수정 요청 스키마
class ProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    profile: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

# 프로필 응답 스키마
class ProfileOut(BaseModel):
    id: int
    nickname: str
    email: Optional[str] = None
    profile: Optional[str] = None

    model_config = {
        "from_attributes": True
    }