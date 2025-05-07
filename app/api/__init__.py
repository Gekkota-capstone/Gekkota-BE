# API 관련 의존성 함수들을 import
# get_current_user: 현재 인증된 사용자 정보를 가져오는 함수
# security: Bearer 토큰 인증을 위한 보안 스키마
from .deps import get_current_user, security

# 모든 API 라우터들을 import
# 각 라우터는 해당 도메인(사용자, 케이지 등)의 API 엔드포인트를 정의
from .routers import (
    user_router,        # 사용자 관리 API
    cage_router,        # 케이지 관리 API
    cleaning_router,    # 청소 관리 API
    health_router,      # 건강 관리 API
    feeding_router,     # 급여 관리 API
    activity_router,    # 활동 관리 API
    camera_router       # 카메라 관리 API
)

# 이 모듈에서 외부로 노출할 이름들을 정의
# from app.api import * 를 사용할 때 이 목록에 있는 것들만 import됨
__all__ = [
    # 인증 관련
    "get_current_user",  # 현재 사용자 정보 조회 함수
    "security",         # Bearer 토큰 인증 스키마
    
    # API 라우터들
    "user_router",      # 사용자 관리 API
    "cage_router",      # 케이지 관리 API
    "cleaning_router",  # 청소 관리 API
    "health_router",    # 건강 관리 API
    "feeding_router",   # 급여 관리 API
    "activity_router",  # 활동 관리 API
    "camera_router"     # 카메라 관리 API
]
