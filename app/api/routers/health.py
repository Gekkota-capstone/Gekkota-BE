from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core import get_db
from app.crud import create_health_record, get_health_records_by_cage, delete_health_record
from app.schemas import HealthCreate, HealthOut
from app.api import get_current_user
from typing import List
from app.schemas.user import ProfileOut

# 건강 기록 관련 라우터 생성 (prefix: /health-records, 태그: health)
router = APIRouter(prefix="/health-records", tags=["health"])

# 건강 기록 생성 엔드포인트 (POST /health-records)
@router.post("", response_model=HealthOut)
def create_health(
    data: HealthCreate,
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 새로운 건강 기록 생성 및 반환
    return create_health_record(db, data)

# 케이지별 건강 기록 조회 엔드포인트 (GET /health-records)
@router.get("", response_model=List[HealthOut])
def get_health(
    cage_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 특정 케이지의 모든 건강 기록 조회
    records = get_health_records_by_cage(db, cage_id)
    # 각 레코드의 photo_urls를 리스트로 변환하여 HealthOut 모델로 변환
    return [HealthOut(
        id=record["id"],
        cage_id=record["cage_id"],
        record_date=record["record_date"],
        weight=record["weight"],
        memo=record["memo"],
        shedding_status=record["shedding_status"],
        photo_urls=record["photo_urls"]  # 이미 리스트로 변환되어 있음
    ) for record in records]

# 건강 기록 삭제 엔드포인트 (DELETE /health-records/{record_id})
@router.delete("/{record_id}", status_code=204)
def delete_health(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 지정된 ID의 건강 기록 삭제
    delete_health_record(db, record_id)
    return