# /service/pet_feed_service.py

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from repository.pet_feed_repository import PetFeedRepository
from datetime import date


class PetFeedService:
    def __init__(self):
        self.repository = PetFeedRepository()

    def create_pet_feed(self, db: Session, firebase_uid: str, pet_id: str, feed_date: date,
                        food_type: str, food_size: Optional[str] = None,
                        food_amount: Optional[float] = None, amount_unit: Optional[str] = None,
                        memo: Optional[str] = None) -> Dict[str, Any]:
        pet_feed = self.repository.create(db, firebase_uid, pet_id, feed_date, food_type,
                                          food_size, food_amount, amount_unit, memo)
        return self._pet_feed_to_dict(pet_feed)

    def get_pet_feed_by_food_type(self, db: Session, firebase_uid: str, pet_id: str,
                                  feed_date: date, food_type: str) -> Optional[Dict[str, Any]]:
        pet_feed = self.repository.get_by_food_type(db, firebase_uid, pet_id, feed_date, food_type)
        if not pet_feed:
            return None
        return self._pet_feed_to_dict(pet_feed)

    def get_pet_feeds_by_date(self, db: Session, firebase_uid: str, pet_id: str,
                              feed_date: date) -> List[Dict[str, Any]]:
        pet_feeds = self.repository.get_by_date(db, firebase_uid, pet_id, feed_date)
        return [self._pet_feed_to_dict(pet_feed) for pet_feed in pet_feeds]

    def get_pet_feeds_by_date_range(self, db: Session, pet_id: str,
                                    start_date: date, end_date: date) -> List[Dict[str, Any]]:
        pet_feeds = self.repository.get_by_date_range(db, pet_id, start_date, end_date)
        return [self._pet_feed_to_dict(pet_feed) for pet_feed in pet_feeds]

    def update_pet_feed_by_food_type(self, db: Session, firebase_uid: str, pet_id: str,
                                     feed_date: date, food_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pet_feed = self.repository.update_by_food_type(db, firebase_uid, pet_id, feed_date, food_type, **data)
        if not pet_feed:
            return None
        return self._pet_feed_to_dict(pet_feed)

    def delete_pet_feed_by_food_type(self, db: Session, firebase_uid: str, pet_id: str,
                                     feed_date: date, food_type: str) -> bool:
        return self.repository.delete_by_food_type(db, firebase_uid, pet_id, feed_date, food_type)

    def _pet_feed_to_dict(self, pet_feed) -> Dict[str, Any]:
        return {
            "pet_id": pet_feed.pet_id,
            "date": pet_feed.date.isoformat() if pet_feed.date else None,
            "food_type": pet_feed.food_type,
            "food_size": pet_feed.food_size,
            "food_amount": pet_feed.food_amount,
            "amount_unit": pet_feed.amount_unit,
            "memo": pet_feed.memo
        }