from sqlalchemy.orm import Session
from app.models import HealthRecord
from app.schemas import HealthCreate
from typing import List, Dict, Any

# 새로운 건강 기록 생성
def create_health_record(db: Session, data: HealthCreate):
    # 건강 기록 객체 생성
    record = HealthRecord(
        cage_id=data.cage_id,
        record_date=data.record_date,
        weight=data.weight,
        memo=data.memo,
        shedding_status=data.shedding_status
    )
    # 사진 URL 리스트 설정
    record.set_photo_list(data.photo_urls)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

# 케이지별 건강 기록 조회
def get_health_records_by_cage(db: Session, cage_id: int) -> List[Dict[str, Any]]:
    # 특정 케이지의 모든 건강 기록 조회
    records = db.query(HealthRecord).filter(HealthRecord.cage_id == cage_id).all()
    result = []
    for record in records:
        # photo_urls가 None이거나 빈 문자열인 경우 빈 리스트 반환
        photo_urls = record.get_photo_list() if record.photo_urls else []
        
        # 모델 객체를 딕셔너리로 변환 (API 응답용)
        record_dict = {
            "id": record.id,
            "cage_id": record.cage_id,
            "record_date": record.record_date,
            "weight": record.weight,
            "memo": record.memo,
            "shedding_status": record.shedding_status,
            "photo_urls": photo_urls
        }
        result.append(record_dict)
    return result

# 건강 기록 삭제
def delete_health_record(db: Session, record_id: int):
    # 건강 기록 조회 및 삭제
    record = db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()