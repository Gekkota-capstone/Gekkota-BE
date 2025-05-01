from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.camera import CameraDataOut
from app.crud import camera as camera_crud

# 카메라 데이터 관련 라우터 생성 (prefix: /camera-data, 태그: camera)
router = APIRouter(prefix="/camera-data", tags=["camera"])

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

# 케이지별 카메라 데이터 조회 엔드포인트 (GET /camera-data)
@router.get("", response_model=list[CameraDataOut])
def get_camera_data(cage_id: int = Query(...), db: Session = Depends(get_db)):
    # 특정 케이지의 모든 카메라 데이터 조회 및 반환
    return camera_crud.get_camera_data_by_cage(db, cage_id)