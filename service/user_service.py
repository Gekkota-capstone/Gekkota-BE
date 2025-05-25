# /service/user_service.py

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from repository.user_repository import UserRepository


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def create_user(self, db: Session, firebase_uid: str, nickname: str, profile: Optional[str] = None) -> Dict[str, Any]:
        user = self.repository.create(db, firebase_uid, nickname, profile)
        return self._user_to_dict(user)

    def get_user(self, db: Session, firebase_uid: str) -> Optional[Dict[str, Any]]:
        user = self.repository.get_by_firebase_uid(db, firebase_uid)
        if not user:
            return None
        return self._user_to_dict(user)

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        users = self.repository.get_all(db, skip, limit)
        return [self._user_to_dict(user) for user in users]

    def update_user(self, db: Session, firebase_uid: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        user = self.repository.update(db, firebase_uid, **data)
        if not user:
            return None
        return self._user_to_dict(user)

    def delete_user(self, db: Session, firebase_uid: str) -> bool:
        return self.repository.delete(db, firebase_uid)

    def _user_to_dict(self, user) -> Dict[str, Any]:
        return {
            "nickname": user.nickname,
            "profile": user.profile
        }