from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import (
    user_router,
    cage_router,
    cleaning_router,
    health_router,
    feeding_router,
    activity_router,
    camera_router
)
from app.core import Base, engine
import app.core.firebase  # Firebase 초기화를 위해 import

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="Gekkota API",
    description="파충류 관리 시스템 API",
    version="1.0.0",
    openapi_tags=[
        {"name": "users", "description": "사용자 관리 API"},
        {"name": "cages", "description": "케이지 관리 API"},
        {"name": "feeding", "description": "급여 관리 API"},
        {"name": "cleaning", "description": "청소 관리 API"},
        {"name": "health", "description": "건강 관리 API"},
        {"name": "camera", "description": "카메라 관리 API"},
        {"name": "activity", "description": "활동량 관리 API"}
    ]
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 등록
app.include_router(user_router)  # 사용자 관리 라우터
app.include_router(cage_router)  # 케이지 관리 라우터
app.include_router(feeding_router)  # 급여 관리 라우터
app.include_router(cleaning_router)  # 청소 관리 라우터
app.include_router(health_router)  # 건강 관리 라우터
app.include_router(camera_router)  # 카메라 관리 라우터
app.include_router(activity_router)  # 활동량 관리 라우터

# 루트 엔드포인트
@app.get("/")
def read_root():
    return {"message": "Welcome to Gekkota API"}