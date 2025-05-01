from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.schemas.health import HealthCreate, HealthOut
from app.crud import health as health_crud
from app.database import SessionLocal
from typing import List

# 건강 기록 관련 라우터 생성 (prefix: /health-records, 태그: health)
router = APIRouter(prefix="/health-records", tags=["health"])

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

# 건강 기록 생성 엔드포인트 (POST /health-records)
@router.post("", response_model=HealthOut)
def create_health(data: HealthCreate, db: Session = Depends(get_db)):
    # 새로운 건강 기록 생성 및 반환
    return health_crud.create_health_record(db, data)

# 케이지별 건강 기록 조회 엔드포인트 (GET /health-records)
@router.get("", response_model=List[HealthOut])
def get_health(cage_id: int = Query(...), db: Session = Depends(get_db)):
    # 특정 케이지의 모든 건강 기록 조회
    records = health_crud.get_health_records_by_cage(db, cage_id)
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
def delete_health(record_id: int, db: Session = Depends(get_db)):
    # 지정된 ID의 건강 기록 삭제
    health_crud.delete_health_record(db, record_id)
    return