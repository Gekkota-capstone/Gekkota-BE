# /repository/pet_clean_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from repository.entity.pet_clean_entity import PetClean
from datetime import date


class PetCleanRepository:
    def create(self, db: Session, firebase_uid: str, pet_id: str,
               clean_date: date, memo: Optional[str] = None) -> PetClean:
        db_pet_clean = PetClean(
            firebase_uid=firebase_uid,
            pet_id=pet_id,
            date=clean_date,
            memo=memo
        )
        db.add(db_pet_clean)
        db.commit()
        db.refresh(db_pet_clean)
        return db_pet_clean

    def get(self, db: Session, firebase_uid: str, pet_id: str, clean_date: date) -> Optional[PetClean]:
        return db.query(PetClean).filter(
            PetClean.firebase_uid == firebase_uid,
            PetClean.pet_id == pet_id,
            PetClean.date == clean_date
        ).first()

    def get_by_pet(self, db: Session, pet_id: str) -> List[PetClean]:
        return db.query(PetClean).filter(PetClean.pet_id == pet_id).all()

    def get_by_user(self, db: Session, firebase_uid: str) -> List[PetClean]:
        return db.query(PetClean).filter(PetClean.firebase_uid == firebase_uid).all()

    def get_by_date_range(self, db: Session, pet_id: str, start_date: date, end_date: date) -> List[PetClean]:
        return db.query(PetClean).filter(
            PetClean.pet_id == pet_id,
            PetClean.date >= start_date,
            PetClean.date <= end_date
        ).all()

    def update(self, db: Session, firebase_uid: str, pet_id: str, clean_date: date,
               **kwargs) -> Optional[PetClean]:
        db_pet_clean = self.get(db, firebase_uid, pet_id, clean_date)
        if db_pet_clean:
            for key, value in kwargs.items():
                setattr(db_pet_clean, key, value)
            db.commit()
            db.refresh(db_pet_clean)
        return db_pet_clean

    def delete(self, db: Session, firebase_uid: str, pet_id: str, clean_date: date) -> bool:
        db_pet_clean = self.get(db, firebase_uid, pet_id, clean_date)
        if db_pet_clean:
            db.delete(db_pet_clean)
            db.commit()
            return True
        return False