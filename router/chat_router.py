# /router/chat_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from router.model.chat_model import ChatQuery, ChatResponse
from service.chat_service import ChatService
from db.session import get_db
from util.firebase_util import get_current_user_firebase_uid

router = APIRouter(prefix="/chats", tags=["chats"])
chat_service = ChatService()


@router.get(
    "/{pet_id}",
    response_model=ChatResponse,
    summary="반려동물 채팅 내역 조회",
    description="특정 반려동물에 대한 모든 채팅 내역을 조회합니다."
)
def read_chats_by_pet(
    pet_id: str,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    """
    Get all chat messages for a specific pet
    """
    return chat_service.get_chats_by_user_and_pet(db, firebase_uid, pet_id)


@router.post(
    "/{pet_id}/query",
    status_code=status.HTTP_201_CREATED,
    summary="반려동물에 대한 질문 처리",
    description="반려동물에 대한 질문을 처리하고 자동으로 답변을 생성합니다."
)
def query_and_save(
    pet_id: str,
    chat_data: ChatQuery,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    """
    Process a query about a pet, generate an answer automatically, and save the chat
    """
    # The create_chat method automatically generates an answer
    chat = chat_service.create_chat(db, firebase_uid, pet_id, chat_data.question)
    return chat