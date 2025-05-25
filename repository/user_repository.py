# /repository/user_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from repository.entity.user_entity import User


class UserRepository:
    def create(self, db: Session, firebase_uid: str, nickname: str, profile: Optional[str] = None) -> User:
        db_user = User(
            firebase_uid=firebase_uid,
            nickname=nickname,
            profile=profile
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_by_firebase_uid(self, db: Session, firebase_uid: str) -> Optional[User]:
        return db.query(User).filter(User.firebase_uid == firebase_uid).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def update(self, db: Session, firebase_uid: str, **kwargs) -> Optional[User]:
        db_user = self.get_by_firebase_uid(db, firebase_uid)
        if db_user:
            for key, value in kwargs.items():
                setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    def delete(self, db: Session, firebase_uid: str) -> bool:
        db_user = self.get_by_firebase_uid(db, firebase_uid)
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False