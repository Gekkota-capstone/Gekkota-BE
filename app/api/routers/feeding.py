from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core import get_db
from app.crud import create_feeding_record, get_feeding_records_by_cage, delete_feeding_record
from app.schemas import FeedingCreate, FeedingOut
from app.api import get_current_user
from typing import List
from app.schemas import ProfileOut

# 먹이 급여 기록 관련 라우터 생성 (prefix: /feeding-records, 태그: feeding)
router = APIRouter(prefix="/feeding-records", tags=["feeding"])

# 먹이 급여 기록 생성 엔드포인트 (POST /feeding-records)
@router.post("", response_model=FeedingOut)
def create_feeding(
    data: FeedingCreate,
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 새로운 먹이 급여 기록 생성 및 반환
    return create_feeding_record(db, data)

# 케이지별 먹이 급여 기록 조회 엔드포인트 (GET /feeding-records)
@router.get("", response_model=List[FeedingOut])
def get_feedings(
    cage_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 특정 케이지의 모든 먹이 급여 기록 조회 및 반환
    return get_feeding_records_by_cage(db, cage_id)

# 먹이 급여 기록 삭제 엔드포인트 (DELETE /feeding-records/{record_id})
@router.delete("/{record_id}")
def delete_feeding(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 지정된 ID의 먹이 급여 기록 삭제
    delete_feeding_record(db, record_id)
    return {"message": "Feeding record deleted successfully"}