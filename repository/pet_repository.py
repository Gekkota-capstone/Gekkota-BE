# /repository/pet_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from repository.entity.pet_entity import Pet
from datetime import date


class PetRepository:
    def create(self, db: Session, pet_id: str, firebase_uid: str, name: str,
               gender: str, species: str, birthdate: Optional[date] = None) -> Pet:
        db_pet = Pet(
            pet_id=pet_id,
            firebase_uid=firebase_uid,
            name=name,
            gender=gender,
            species=species,
            birthdate=birthdate
        )
        db.add(db_pet)
        db.commit()
        db.refresh(db_pet)
        return db_pet

    def get_by_id(self, db: Session, pet_id: str) -> Optional[Pet]:
        return db.query(Pet).filter(Pet.pet_id == pet_id).first()

    def get_by_user(self, db: Session, firebase_uid: str) -> List[Pet]:
        return db.query(Pet).filter(Pet.firebase_uid == firebase_uid).all()

    def update(self, db: Session, firebase_uid: str, pet_id: str, **kwargs) -> Optional[Pet]:
        db_pet = db.query(Pet).filter(
            Pet.pet_id == pet_id,
            Pet.firebase_uid == firebase_uid
        ).first()

        if db_pet:
            for key, value in kwargs.items():
                setattr(db_pet, key, value)
            db.commit()
            db.refresh(db_pet)
        return db_pet

    def delete(self, db: Session, pet_id: str) -> bool:
        db_pet = self.get_by_id(db, pet_id)
        if db_pet:
            db.delete(db_pet)
            db.commit()
            return True
        return False