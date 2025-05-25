# /repository/pet_feed_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from repository.entity.pet_feed_entity import PetFeed
from datetime import date


class PetFeedRepository:
    def create(self, db: Session, firebase_uid: str, pet_id: str, feed_date: date,
               food_type: str, food_size: Optional[str] = None, food_amount: Optional[float] = None,
               amount_unit: Optional[str] = None, memo: Optional[str] = None) -> PetFeed:
        db_pet_feed = PetFeed(
            firebase_uid=firebase_uid,
            pet_id=pet_id,
            date=feed_date,
            food_type=food_type,
            food_size=food_size,
            food_amount=food_amount,
            amount_unit=amount_unit,
            memo=memo
        )
        db.add(db_pet_feed)
        db.commit()
        db.refresh(db_pet_feed)
        return db_pet_feed

    def get_by_food_type(self, db: Session, firebase_uid: str, pet_id: str,
                         feed_date: date, food_type: str) -> Optional[PetFeed]:
        return db.query(PetFeed).filter(
            PetFeed.firebase_uid == firebase_uid,
            PetFeed.pet_id == pet_id,
            PetFeed.date == feed_date,
            PetFeed.food_type == food_type
        ).first()

    def get_by_date(self, db: Session, firebase_uid: str, pet_id: str, feed_date: date) -> List[PetFeed]:
        return db.query(PetFeed).filter(
            PetFeed.firebase_uid == firebase_uid,
            PetFeed.pet_id == pet_id,
            PetFeed.date == feed_date
        ).all()

    def get_by_date_range(self, db: Session, pet_id: str, start_date: date, end_date: date) -> List[PetFeed]:
        return db.query(PetFeed).filter(
            PetFeed.pet_id == pet_id,
            PetFeed.date >= start_date,
            PetFeed.date <= end_date
        ).all()

    def update_by_food_type(self, db: Session, firebase_uid: str, pet_id: str, feed_date: date,
                            food_type: str, **kwargs) -> Optional[PetFeed]:
        db_pet_feed = self.get_by_food_type(db, firebase_uid, pet_id, feed_date, food_type)
        if db_pet_feed:
            for key, value in kwargs.items():
                setattr(db_pet_feed, key, value)
            db.commit()
            db.refresh(db_pet_feed)
        return db_pet_feed

    def delete_by_food_type(self, db: Session, firebase_uid: str, pet_id: str,
                            feed_date: date, food_type: str) -> bool:
        db_pet_feed = self.get_by_food_type(db, firebase_uid, pet_id, feed_date, food_type)
        if db_pet_feed:
            db.delete(db_pet_feed)
            db.commit()
            return True
        return False