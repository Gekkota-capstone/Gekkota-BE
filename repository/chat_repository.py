# /repository/chat_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from repository.entity.chat_entity import Chat


class ChatRepository:
    def create(self, db: Session, firebase_uid: str, question: str, answer: Optional[str] = None) -> Chat:
        db_chat = Chat(
            firebase_uid=firebase_uid,
            question=question,
            answer=answer
        )
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat

    def get_by_id(self, db: Session, chat_id: int) -> Optional[Chat]:
        return db.query(Chat).filter(Chat.id == chat_id).first()

    def get_by_user(self, db: Session, firebase_uid: str) -> List[Chat]:
        return db.query(Chat).filter(Chat.firebase_uid == firebase_uid).all()

    def update(self, db: Session, chat_id: int, **kwargs) -> Optional[Chat]:
        db_chat = self.get_by_id(db, chat_id)
        if db_chat:
            for key, value in kwargs.items():
                setattr(db_chat, key, value)
            db.commit()
            db.refresh(db_chat)
        return db_chat

    def delete(self, db: Session, chat_id: int) -> bool:
        db_chat = self.get_by_id(db, chat_id)
        if db_chat:
            db.delete(db_chat)
            db.commit()
            return True
        return False