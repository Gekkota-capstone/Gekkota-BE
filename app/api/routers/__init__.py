# 각 라우터 모듈에서 router 객체를 가져와서 더 명확한 이름으로 재정의
# 예: user.py의 router를 user_router로, cage.py의 router를 cage_router로 import
from .user import router as user_router
from .cage import router as cage_router
from .cleaning import router as cleaning_router
from .health import router as health_router
from .feeding import router as feeding_router
from .activity import router as activity_router
from .camera import router as camera_router

# __all__은 이 모듈에서 외부로 노출할 이름들을 정의
# from app.api.routers import * 를 사용할 때 이 목록에 있는 것들만 import됨
__all__ = [
    "user_router",        # 사용자 관련 API 라우터
    "cage_router",        # 케이지 관련 API 라우터
    "cleaning_router",    # 청소 관련 API 라우터
    "health_router",      # 건강 관련 API 라우터
    "feeding_router",     # 급여 관련 API 라우터
    "activity_router",    # 활동 관련 API 라우터
    "camera_router"       # 카메라 관련 API 라우터
]
