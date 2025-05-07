# Pydantic 스키마 클래스들을 import
from .user import ProfileCreate, ProfileUpdate, ProfileOut                              # 사용자 관련 스키마
from .cage import CageCreate, CageUpdate, CageOut, CageListResponse, CageStateResponse  # 케이지 관련 스키마
from .cleaning import CleaningCreate, CleaningOut, CleaningCycleUpdate                  # 청소 관련 스키마
from .health import HealthCreate, HealthOut                                             # 건강 관련 스키마
from .feeding import FeedingCreate, FeedingOut                                          # 급여 관련 스키마
from .activity import ActivityDataOut                                                   # 활동 관련 스키마
from .camera import CameraDataOut                                                       # 카메라 관련 스키마

# 이 모듈에서 외부로 노출할 이름들을 정의
# from app.schemas import * 를 사용할 때 이 목록에 있는 것들만 import됨
__all__ = [
    # User 관련 스키마
    "ProfileCreate", "ProfileUpdate", "ProfileOut",
    
    # Cage 관련 스키마
    "CageCreate", "CageUpdate", "CageOut", "CageListResponse", "CageStateResponse",
    
    # Cleaning 관련 스키마
    "CleaningCreate", "CleaningOut", "CleaningCycleUpdate",
    
    # Health 관련 스키마
    "HealthCreate", "HealthOut",
    
    # Feeding 관련 스키마
    "FeedingCreate", "FeedingOut",
    
    # Activity 관련 스키마
    "ActivityDataOut",
    
    # Camera 관련 스키마
    "CameraDataOut"
]