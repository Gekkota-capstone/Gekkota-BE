# /repository/pet_active_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from repository.entity.pet_active_entity import PetActive
from datetime import datetime


class PetActiveRepository:
    def create(self, db: Session, firebase_uid: str, pet_id: str,
               abnormalBehavior: Optional[str] = None,
               highlightVideoUrl: Optional[str] = None,
               bioPattern: Optional[str] = None,
               heatmapImageUrl: Optional[str] = None,
               timeOfActivity: Optional[str] = None,
               recentDatOfActivity: Optional[datetime] = None) -> PetActive:
        db_pet_active = PetActive(
            firebase_uid=firebase_uid,
            pet_id=pet_id,
            abnormalBehavior=abnormalBehavior,
            highlightVideoUrl=highlightVideoUrl,
            bioPattern=bioPattern,
            heatmapImageUrl=heatmapImageUrl,
            timeOfActivity=timeOfActivity,
            recentDatOfActivity=recentDatOfActivity
        )
        db.add(db_pet_active)
        db.commit()
        db.refresh(db_pet_active)
        return db_pet_active

    def get(self, db: Session, firebase_uid: str, pet_id: str) -> Optional[PetActive]:
        return db.query(PetActive).filter(
            PetActive.firebase_uid == firebase_uid,
            PetActive.pet_id == pet_id
        ).first()

    def get_by_pet(self, db: Session, pet_id: str) -> Optional[PetActive]:
        return db.query(PetActive).filter(PetActive.pet_id == pet_id).first()

    def get_by_user(self, db: Session, firebase_uid: str) -> List[PetActive]:
        return db.query(PetActive).filter(PetActive.firebase_uid == firebase_uid).all()

    def update(self, db: Session, firebase_uid: str, pet_id: str, **kwargs) -> Optional[PetActive]:
        db_pet_active = self.get(db, firebase_uid, pet_id)
        if db_pet_active:
            for key, value in kwargs.items():
                setattr(db_pet_active, key, value)
            db.commit()
            db.refresh(db_pet_active)
        return db_pet_active

    def delete(self, db: Session, firebase_uid: str, pet_id: str) -> bool:
        db_pet_active = self.get(db, firebase_uid, pet_id)
        if db_pet_active:
            db.delete(db_pet_active)
            db.commit()
            return True
        return False