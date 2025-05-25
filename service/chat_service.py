# /service/chat_service.py

from sqlalchemy.orm import Session
from typing import List, Dict, Any
from repository.chat_repository import ChatRepository
import sys
import os

# llm_api 모듈 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from llm_api.rag_qa_prompt import handle_query as rag_handle_query


class ChatService:
    def __init__(self):
        self.repository = ChatRepository()

    def create_chat(self, db: Session, firebase_uid: str, pet_id: str, question: str) -> Dict[str, Any]:
        """
        Create a new chat entry with generated answer
        """
        # Generate answer using RAG system
        try:
            answer = rag_handle_query(question, pet_id, firebase_uid, db)
        except Exception as e:
            print(f"RAG 시스템 오류: {e}")
            answer = "죄송합니다. 현재 시스템에 문제가 발생했습니다. 잠시 후 다시 시도해주세요."

        # Create chat in repository
        chat = self.repository.create(db, firebase_uid, question, answer)
        return self._chat_to_dict(chat)

    def get_chats_by_user_and_pet(self, db: Session, firebase_uid: str, pet_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all chats for a specific user (pet_id는 현재 사용하지 않지만 향후 확장 가능)
        """
        # Get all chats for the user
        chats = self.repository.get_by_user(db, firebase_uid)

        # Convert to dict format and wrap in messages array
        messages = [self._chat_to_dict(chat) for chat in chats]
        return {"messages": messages}

    def _chat_to_dict(self, chat) -> Dict[str, Any]:
        return {
            "id": chat.id,
            "question": chat.question,
            "answer": chat.answer,
            "created_at": chat.created_at.isoformat() if chat.created_at else None
        }