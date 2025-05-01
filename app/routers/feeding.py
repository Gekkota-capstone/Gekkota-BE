from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.feeding import FeedingCreate, FeedingOut
from app.crud import feeding as feeding_crud
from app.database import SessionLocal

# 먹이 급여 기록 관련 라우터 생성 (prefix: /feeding-records, 태그: feeding)
router = APIRouter(prefix="/feeding-records", tags=["feeding"])

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

# 먹이 급여 기록 생성 엔드포인트 (POST /feeding-records)
@router.post("", response_model=FeedingOut)
def create_feeding(data: FeedingCreate, db: Session = Depends(get_db)):
    # 새로운 먹이 급여 기록 생성 및 반환
    return feeding_crud.create_feeding_record(db, data)

# 케이지별 먹이 급여 기록 조회 엔드포인트 (GET /feeding-records)
@router.get("", response_model=list[FeedingOut])
def list_feedings(cage_id: int = Query(...), db: Session = Depends(get_db)):
    # 특정 케이지의 모든 먹이 급여 기록 조회 및 반환
    return feeding_crud.get_feeding_records_by_cage(db, cage_id)

# 먹이 급여 기록 삭제 엔드포인트 (DELETE /feeding-records/{record_id})
@router.delete("/{record_id}", status_code=204)
def delete_feeding(record_id: int, db: Session = Depends(get_db)):
    # 지정된 ID의 먹이 급여 기록 삭제
    feeding_crud.delete_feeding_record(db, record_id)
    return