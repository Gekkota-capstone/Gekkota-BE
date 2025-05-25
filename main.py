# main.py

from fastapi import FastAPI
import asyncio
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# DB 관련 임포트
from db.session import get_db
from db.database import Base, engine

# LLM 시스템 초기화
from llm_api.rag_qa_prompt import init_llm_system
init_llm_system()

# 유틸리티 임포트
from util.config_util import setup_test_mode
from util.swagger_util import setup_swagger
from util.scheduler import run_every_5_minutes, run_daily_at_midnight
from util.active_create import process_current_interval

# 서비스 임포트
from service.heatmap_service import HeatmapService

# 엔티티 임포트 (스키마 생성용)
from repository.entity import (
    user_entity,
    pet_entity,
    device_entity,
    pet_clean_entity,
    pet_feed_entity,
    pet_health_entity,
    pet_active_entity,
    chat_entity
)

# 라우터 임포트
from router.user_router import router as user_router
from router.pet_router import router as pet_router
from router.device_router import router as device_router
from router.device_router import cam_router
from router.pet_clean_router import router as pet_clean_router
from router.pet_feed_router import router as pet_feed_router
from router.pet_health_router import router as pet_health_router
from router.pet_active_router import router as pet_active_router
from router.chat_router import router as chat_router
from router.s3_router import router as s3_router, cam_router as s3_cam_router
from router.heatmap_router import router as heatmap_router

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Direp Capstone",
    description="capstone api",
    version="0.1.0"
)

# 테스트 모드 설정 (개발 환경에서만 True로 설정)
setup_test_mode(True)  # 개발 중에는 True, 배포 시 False로 변경

# Swagger UI 설정
setup_swagger(app)

# 5분마다 실행될 활동량 데이터 처리 함수
def run_activity_process(start_time, end_time):
    """활동량 데이터 처리 함수"""
    # 데이터베이스 세션 생성
    session = next(get_db())
    try:
        logger.info(f"Running activity data processing for {start_time} to {end_time}...")
        process_current_interval(session, start_time, end_time)
    except Exception as e:
        logger.error(f"Error in activity data processing: {e}")
    finally:
        session.close()

# 매일 자정에 실행될 히트맵 생성 함수
def run_daily_heatmap_generation():
    """매일 자정에 전날 데이터로 히트맵 생성"""
    # 데이터베이스 세션 생성
    session = next(get_db())
    try:
        logger.info("Running daily heatmap generation...")
        heatmap_service = HeatmapService()
        result = heatmap_service.generate_previous_day_heatmap(session)
        if result["success"]:
            logger.info(f"Daily heatmap generated successfully: {result['url']}")
        else:
            logger.error(f"Daily heatmap generation failed: {result['message']}")
    except Exception as e:
        logger.error(f"Error in daily heatmap generation: {e}")
    finally:
        session.close()

# Include routers
app.include_router(user_router)
app.include_router(pet_router)
app.include_router(device_router)
app.include_router(cam_router)
app.include_router(pet_clean_router)
app.include_router(pet_feed_router)
app.include_router(pet_health_router)
app.include_router(pet_active_router)
app.include_router(chat_router)
app.include_router(s3_router)
app.include_router(s3_cam_router)
app.include_router(heatmap_router)


@app.on_event("startup")
async def startup_event():
    """앱 시작 시 백그라운드 태스크 시작"""
    # 5분마다 실행할 활동량 데이터 처리 태스크 설정
    asyncio.create_task(run_every_5_minutes(run_activity_process))

    # 매일 자정에 실행할 히트맵 생성 태스크 설정
    asyncio.create_task(run_daily_at_midnight(run_daily_heatmap_generation))

    logger.info("Scheduled background tasks started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)