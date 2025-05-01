from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.activity import ActivityDataOut
from app.crud import activity as activity_crud

# 활동 데이터 관련 라우터 생성 (prefix: /activity-data, 태그: activity)
router = APIRouter(prefix="/activity-data", tags=["activity"])

# 데이터베이스 세션 의존성 함수
def get_db():
    # 새로운 데이터베이스 세션 생성
    db = SessionLocal()
    try:
        # 세션을 yield하여 라우터에서 사용할 수 있게 함
        yield db
    finally:
        # 요청 처리가 끝나면 세션을 닫음
        db.close()

# 카메라 데이터별 활동 데이터 조회 엔드포인트 (GET /activity-data)
@router.get("", response_model=list[ActivityDataOut])
def get_activity_data(camera_data_id: int = Query(...), db: Session = Depends(get_db)):
    # 특정 카메라 데이터의 모든 활동 데이터 조회 및 반환
    return activity_crud.get_activity_by_camera_id(db, camera_data_id)