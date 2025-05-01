from fastapi import FastAPI
from app.routers import user, cage, feeding, cleaning, health, camera, activity, notification
from app.auth import google
from app.database import engine, Base

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 라우터 등록
app.include_router(google.router)  # Google OAuth 인증 라우터
app.include_router(user.router)  # 사용자 관리 라우터
app.include_router(cage.router)  # 케이지 관리 라우터
app.include_router(feeding.router)  # 급여 관리 라우터
app.include_router(cleaning.router)  # 청소 관리 라우터
app.include_router(health.router)  # 건강 관리 라우터
app.include_router(camera.router)  # 카메라 관리 라우터
app.include_router(activity.router)  # 활동량 관리 라우터
app.include_router(notification.router)  # 알림 설정 라우터