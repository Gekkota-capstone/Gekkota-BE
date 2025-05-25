# /service/pet_clean_service.py

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from repository.pet_clean_repository import PetCleanRepository
from datetime import date


class PetCleanService:
    def __init__(self):
        self.repository = PetCleanRepository()

    def create_pet_clean(self, db: Session, firebase_uid: str, pet_id: str,
                         clean_date: date, memo: Optional[str] = None) -> Dict[str, Any]:
        pet_clean = self.repository.create(db, firebase_uid, pet_id, clean_date, memo)
        return self._pet_clean_to_dict(pet_clean)

    def get_pet_clean(self, db: Session, firebase_uid: str, pet_id: str,
                      clean_date: date) -> Optional[Dict[str, Any]]:
        pet_clean = self.repository.get(db, firebase_uid, pet_id, clean_date)
        if not pet_clean:
            return None
        return self._pet_clean_to_dict(pet_clean)

    def get_pet_cleans_by_date_range(self, db: Session, pet_id: str,
                                     start_date: date, end_date: date) -> List[Dict[str, Any]]:
        pet_cleans = self.repository.get_by_date_range(db, pet_id, start_date, end_date)
        return [self._pet_clean_to_dict(pet_clean) for pet_clean in pet_cleans]

    def update_pet_clean(self, db: Session, firebase_uid: str, pet_id: str,
                         clean_date: date, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pet_clean = self.repository.update(db, firebase_uid, pet_id, clean_date, **data)
        if not pet_clean:
            return None
        return self._pet_clean_to_dict(pet_clean)

    def delete_pet_clean(self, db: Session, firebase_uid: str, pet_id: str, clean_date: date) -> bool:
        return self.repository.delete(db, firebase_uid, pet_id, clean_date)

    def _pet_clean_to_dict(self, pet_clean) -> Dict[str, Any]:
        return {
            "pet_id": pet_clean.pet_id,
            "date": pet_clean.date.isoformat() if pet_clean.date else None,
            "memo": pet_clean.memo
        }