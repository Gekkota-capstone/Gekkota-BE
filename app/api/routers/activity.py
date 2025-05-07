from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core import get_db
from app.api import get_current_user
from app.schemas import ActivityDataOut
from app.crud import get_activity_by_camera_id

# 활동 데이터 관련 라우터 생성 (prefix: /activity-data, 태그: activity)
router = APIRouter(prefix="/activity-data", tags=["activity"])

# 카메라 데이터별 활동 데이터 조회 엔드포인트 (GET /activity-data)
@router.get("", response_model=list[ActivityDataOut])
def get_activity_data(
    camera_data_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 특정 카메라 데이터의 모든 활동 데이터 조회 및 반환
    return get_activity_by_camera_id(db, camera_data_id)