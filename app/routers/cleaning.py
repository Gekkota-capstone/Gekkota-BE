from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.schemas.cleaning import CleaningCreate, CleaningOut, CleaningCycleUpdate
from app.crud import cleaning as cleaning_crud
from app.database import SessionLocal

# 청소 기록 관련 라우터 생성 (prefix: /cleaning-records, 태그: cleaning)
router = APIRouter(prefix="/cleaning-records", tags=["cleaning"])

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

# 청소 기록 생성 엔드포인트 (POST /cleaning-records)
@router.post("", response_model=CleaningOut)
def create_cleaning(data: CleaningCreate, db: Session = Depends(get_db)):
    # 새로운 청소 기록 생성 및 반환
    return cleaning_crud.create_cleaning_record(db, data)

# 케이지별 청소 기록 조회 엔드포인트 (GET /cleaning-records)
@router.get("", response_model=list[CleaningOut])
def get_cleanings(cage_id: int = Query(...), db: Session = Depends(get_db)):
    # 특정 케이지의 모든 청소 기록 조회 및 반환
    return cleaning_crud.get_cleaning_records_by_cage(db, cage_id)

# 청소 기록 삭제 엔드포인트 (DELETE /cleaning-records/{record_id})
@router.delete("/{record_id}", status_code=204)
def delete_cleaning(record_id: int, db: Session = Depends(get_db)):
    # 지정된 ID의 청소 기록 삭제
    cleaning_crud.delete_cleaning_record(db, record_id)
    return