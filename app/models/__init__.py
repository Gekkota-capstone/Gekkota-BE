# 데이터베이스 모델 클래스들을 import
from .user import User                # 사용자 모델
from .cage import Cage                # 케이지 모델
from .cleaning import CleaningRecord  # 청소 기록 모델
from .health import HealthRecord      # 건강 기록 모델
from .feeding import FeedingRecord    # 급여 기록 모델
from .activity import ActivityData    # 활동 데이터 모델
from .camera import CameraData        # 카메라 데이터 모델

# 이 모듈에서 외부로 노출할 이름들을 정의
# from app.models import * 를 사용할 때 이 목록에 있는 것들만 import됨
__all__ = [
    "User",           # 사용자 모델
    "Cage",           # 케이지 모델
    "CleaningRecord", # 청소 기록 모델
    "HealthRecord",   # 건강 기록 모델
    "FeedingRecord",  # 급여 기록 모델
    "ActivityData",   # 활동 데이터 모델
    "CameraData"      # 카메라 데이터 모델
]
