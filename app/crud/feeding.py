from sqlalchemy.orm import Session
from app.models import FeedingRecord
from app.schemas import FeedingCreate

# 새로운 먹이 급여 기록 생성
def create_feeding_record(db: Session, data: FeedingCreate):
    # 먹이 급여 기록 객체 생성 및 저장
    record = FeedingRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

# 케이지별 먹이 급여 기록 조회
def get_feeding_records_by_cage(db: Session, cage_id: int):
    return db.query(FeedingRecord).filter(FeedingRecord.cage_id == cage_id).all()

# 먹이 급여 기록 삭제
def delete_feeding_record(db: Session, record_id: int):
    # 먹이 급여 기록 조회 및 삭제
    record = db.query(FeedingRecord).filter(FeedingRecord.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()