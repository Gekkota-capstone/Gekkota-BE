from sqlalchemy.orm import Session
from app.models import CleaningRecord
from app.models import Cage
from app.schemas import CleaningCreate

# 새로운 청소 기록 생성
def create_cleaning_record(db: Session, data: CleaningCreate):
    # 청소 기록 객체 생성 및 저장
    record = CleaningRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

# 케이지별 청소 기록 조회
def get_cleaning_records_by_cage(db: Session, cage_id: int):
    return db.query(CleaningRecord).filter(CleaningRecord.cage_id == cage_id).all()

# 청소 기록 삭제
def delete_cleaning_record(db: Session, record_id: int):
    # 청소 기록 조회 및 삭제
    record = db.query(CleaningRecord).filter(CleaningRecord.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()

# 케이지의 청소 주기 업데이트
def update_cleaning_cycle(db: Session, cage_id: int, cycle_update):
    # 케이지 조회 및 청소 주기 업데이트
    cage = db.query(Cage).filter(Cage.id == cage_id).first()
    if cage:
        cage.cleaning_cycle = cycle_update.cleaning_cycle
        db.commit()
        db.refresh(cage)
    return cage