from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core import get_db
from app.crud import create_cleaning_record, get_cleaning_records_by_cage, delete_cleaning_record
from app.schemas import CleaningCreate, CleaningOut, ProfileOut
from app.api import get_current_user
from typing import List

# 청소 기록 관련 라우터 생성 (prefix: /cleaning-records, 태그: cleaning)
router = APIRouter(prefix="/cleaning-records", tags=["cleaning"])

# 청소 기록 생성 엔드포인트 (POST /cleaning-records)
@router.post("", response_model=CleaningOut)
def create_cleaning(
    data: CleaningCreate,
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 새로운 청소 기록 생성 및 반환
    return create_cleaning_record(db, data)

# 케이지별 청소 기록 조회 엔드포인트 (GET /cleaning-records)
@router.get("", response_model=List[CleaningOut])
def get_cleanings(
    cage_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 특정 케이지의 모든 청소 기록 조회
    return get_cleaning_records_by_cage(db, cage_id)

# 청소 기록 삭제 엔드포인트 (DELETE /cleaning-records/{record_id})
@router.delete("/{record_id}")
def delete_cleaning(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 지정된 ID의 청소 기록 삭제
    delete_cleaning_record(db, record_id)
    return {"message": "Cleaning record deleted successfully"}