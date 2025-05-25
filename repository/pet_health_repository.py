# /repository/pet_health_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from repository.entity.pet_health_entity import PetHealth
from datetime import date


class PetHealthRepository:
    def create(self, db: Session, firebase_uid: str, pet_id: str, health_date: date,
               weight: Optional[float] = None, memo: Optional[str] = None,
               shedding_status: Optional[str] = None) -> PetHealth:
        db_pet_health = PetHealth(
            firebase_uid=firebase_uid,
            pet_id=pet_id,
            date=health_date,
            weight=weight,
            memo=memo,
            shedding_status=shedding_status
        )
        db.add(db_pet_health)
        db.commit()
        db.refresh(db_pet_health)
        return db_pet_health

    def get(self, db: Session, firebase_uid: str, pet_id: str, health_date: date) -> Optional[PetHealth]:
        return db.query(PetHealth).filter(
            PetHealth.firebase_uid == firebase_uid,
            PetHealth.pet_id == pet_id,
            PetHealth.date == health_date
        ).first()

    def get_by_pet(self, db: Session, pet_id: str) -> List[PetHealth]:
        return db.query(PetHealth).filter(PetHealth.pet_id == pet_id).all()

    def get_by_user(self, db: Session, firebase_uid: str) -> List[PetHealth]:
        return db.query(PetHealth).filter(PetHealth.firebase_uid == firebase_uid).all()

    def get_by_date_range(self, db: Session, pet_id: str, start_date: date, end_date: date) -> List[PetHealth]:
        return db.query(PetHealth).filter(
            PetHealth.pet_id == pet_id,
            PetHealth.date >= start_date,
            PetHealth.date <= end_date
        ).all()

    def update(self, db: Session, firebase_uid: str, pet_id: str, health_date: date,
               **kwargs) -> Optional[PetHealth]:
        db_pet_health = self.get(db, firebase_uid, pet_id, health_date)
        if db_pet_health:
            for key, value in kwargs.items():
                setattr(db_pet_health, key, value)
            db.commit()
            db.refresh(db_pet_health)
        return db_pet_health

    def delete(self, db: Session, firebase_uid: str, pet_id: str, health_date: date) -> bool:
        db_pet_health = self.get(db, firebase_uid, pet_id, health_date)
        if db_pet_health:
            db.delete(db_pet_health)
            db.commit()
            return True
        return False