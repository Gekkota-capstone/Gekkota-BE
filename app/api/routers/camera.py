from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core import get_db
from app.schemas import CameraDataOut
from app.crud import get_camera_data_by_cage
from app.api import get_current_user
from app.schemas import ProfileOut

# 카메라 데이터 관련 라우터 생성 (prefix: /camera-data, 태그: camera)
router = APIRouter(prefix="/camera-data", tags=["camera"])

# 케이지별 카메라 데이터 조회 엔드포인트 (GET /camera-data)
@router.get("", response_model=list[CameraDataOut])
def get_camera_data(
    cage_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 특정 케이지의 모든 카메라 데이터 조회 및 반환
    return get_camera_data_by_cage(db, cage_id)