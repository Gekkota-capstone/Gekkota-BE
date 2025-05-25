# /router/pet_active_router.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional

from router.model.pet_active_model import PetActiveResponse
from service.pet_active_service import PetActiveService
from db.session import get_db
from util.firebase_util import get_current_user_firebase_uid

router = APIRouter(prefix="/pet-actives", tags=["pet-actives"])
pet_active_service = PetActiveService()

@router.get(
    "/{pet_id}",
    response_model=PetActiveResponse,
    summary="반려동물 활동 정보 조회",
    description="지정된 반려동물에 대한 활동 정보를 조회합니다."
)
def read_pet_active(
    pet_id: str,
    query_date: Optional[date] = Query(None, description="조회 날짜 (기본값: 오늘)"),
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    # 반려동물 상태 조회
    state = pet_active_service.get_pet_active(db, firebase_uid, pet_id, query_date)
    return state