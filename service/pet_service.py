# /service/pet_service.py

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from repository.pet_repository import PetRepository
import uuid
from datetime import date


class PetService:
    def __init__(self):
        self.repository = PetRepository()

    def create_pet(self, db: Session, firebase_uid: str, name: str, gender: str,
                   species: str, birthdate: Optional[date] = None) -> Dict[str, Any]:
        # Generate a unique pet_id
        pet_id = str(uuid.uuid4())

        pet = self.repository.create(db, pet_id, firebase_uid, name, gender, species, birthdate)
        return self._pet_to_dict(pet)

    def get_pet(self, db: Session, pet_id: str) -> Optional[Dict[str, Any]]:
        pet = self.repository.get_by_id(db, pet_id)
        if not pet:
            return None
        return self._pet_to_dict(pet)

    def get_pets_by_user(self, db: Session, firebase_uid: str) -> List[Dict[str, Any]]:
        pets = self.repository.get_by_user(db, firebase_uid)
        return [self._pet_to_dict(pet) for pet in pets]

    def update_pet(self, db: Session, firebase_uid: str, pet_id: str,
                   data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pet = self.repository.update(db, firebase_uid, pet_id, **data)
        if not pet:
            return None
        return self._pet_to_dict(pet)

    def delete_pet(self, db: Session, pet_id: str) -> bool:
        return self.repository.delete(db, pet_id)

    def _pet_to_dict(self, pet) -> Dict[str, Any]:
        return {
            "pet_id": pet.pet_id,
            "name": pet.name,
            "gender": pet.gender,
            "species": pet.species,
            "birthdate": pet.birthdate.isoformat() if pet.birthdate else None
        }