from sqlalchemy.orm import Session
from app.models import Cage
from app.schemas import CageCreate, CageUpdate

# 케이지 ID로 케이지 조회
def get_cage(db: Session, cage_id: int):
    return db.query(Cage).filter(Cage.id == cage_id).first()

# 사용자의 모든 케이지 조회
def get_user_cages(db: Session, user_id: int):
    return db.query(Cage).filter(Cage.user_id == user_id).all()

# 새로운 케이지 생성
def create_cage(db: Session, user_id: int, cage: CageCreate):
    cage_data = cage.model_dump()
    # cleaning_cycle이 None인 경우 -1로 설정 (청소 주기가 설정되지 않음을 의미)
    if cage_data.get('cleaning_cycle') is None:
        cage_data['cleaning_cycle'] = -1
    
    # 새로운 케이지 객체 생성 및 저장
    db_cage = Cage(**cage_data, user_id=user_id)
    db.add(db_cage)
    db.commit()
    db.refresh(db_cage)
    return db_cage

# 케이지 정보 업데이트
def update_cage(db: Session, cage_id: int, cage: CageUpdate):
    # 기존 케이지 조회
    db_cage = db.query(Cage).filter(Cage.id == cage_id).first()
    if db_cage:
        # 변경된 필드만 업데이트
        for key, value in cage.model_dump(exclude_unset=True).items():
            setattr(db_cage, key, value)
        db.commit()
        db.refresh(db_cage)
    return db_cage

# 케이지 삭제
def delete_cage(db: Session, cage_id: int):
    # 케이지 조회 및 삭제
    db_cage = db.query(Cage).filter(Cage.id == cage_id).first()
    if db_cage:
        db.delete(db_cage)
        db.commit()
        return True
    return False