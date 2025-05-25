# /router/pet_feed_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from router.model.pet_feed_model import PetFeedCreate, PetFeedUpdate, PetFeedResponse
from service.pet_feed_service import PetFeedService
from db.session import get_db
from util.firebase_util import get_current_user_firebase_uid

router = APIRouter(prefix="/pet-feeds", tags=["pet-feeds"])
pet_feed_service = PetFeedService()


@router.post(
    "/{pet_id}",
    response_model=PetFeedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="반려동물 먹이 기록 생성",
    description="지정된 반려동물 ID에 대한 먹이 기록을 생성합니다."
)
def create_pet_feed(
    pet_id: str,
    pet_feed_data: PetFeedCreate,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    # 동일 날짜 + 동일 food_type 중복 체크
    existing_pet_feed = pet_feed_service.get_pet_feed_by_food_type(
        db, firebase_uid, pet_id, pet_feed_data.date, pet_feed_data.food_type
    )

    if existing_pet_feed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pet feed record already exists for this date and food type"
        )

    return pet_feed_service.create_pet_feed(
        db, firebase_uid, pet_id,
        pet_feed_data.date, pet_feed_data.food_type, pet_feed_data.food_size,
        pet_feed_data.food_amount, pet_feed_data.amount_unit, pet_feed_data.memo
    )


@router.get(
    "/{pet_id}",
    response_model=List[PetFeedResponse],
    summary="반려동물 먹이 기록 조회",
    description="지정된 반려동물 ID와 날짜에 대한 먹이 기록을 조회합니다."
)
def read_pet_feed(
    pet_id: str,
    date: date = Query(..., description="먹이 기록 날짜"),
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    pet_feeds = pet_feed_service.get_pet_feeds_by_date(db, firebase_uid, pet_id, date)
    if not pet_feeds:
        return [{
            "pet_id": pet_id,
            "date": date,
            "food_type": None,
            "food_size": None,
            "food_amount": None,
            "amount_unit": None,
            "memo": None
        }]
    return pet_feeds


@router.get(
    "/{pet_id}/date-range",
    response_model=List[PetFeedResponse],
    summary="날짜 범위로 반려동물 먹이 기록 조회",
    description="지정된 반려동물 ID와 날짜 범위에 대한 먹이 기록을 조회합니다."
)
def read_pet_feeds_by_date_range(
    pet_id: str,
    start_date: date = Query(..., description="시작 날짜"),
    end_date: date = Query(..., description="종료 날짜"),
    db: Session = Depends(get_db)
):
    pet_feeds = pet_feed_service.get_pet_feeds_by_date_range(db, pet_id, start_date, end_date)
    return pet_feeds


@router.put(
    "/{pet_id}",
    response_model=PetFeedResponse,
    summary="반려동물 먹이 기록 수정",
    description="지정된 반려동물 ID, 날짜, food_type에 대한 먹이 기록을 수정합니다."
)
def update_pet_feed(
    pet_id: str,
    pet_feed_data: PetFeedUpdate,
    date: date = Query(..., description="먹이 기록 날짜"),
    food_type: str = Query(..., description="음식 타입"),
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    updated_pet_feed = pet_feed_service.update_pet_feed_by_food_type(
        db, firebase_uid, pet_id, date, food_type, pet_feed_data.dict(exclude_unset=True)
    )

    if updated_pet_feed is None:
        return {
            "pet_id": pet_id,
            "date": date,
            "food_type": None,
            "food_size": None,
            "food_amount": None,
            "amount_unit": None,
            "memo": None
        }
    return updated_pet_feed


@router.delete(
    "/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="반려동물 먹이 기록 삭제",
    description="지정된 반려동물 ID, 날짜, food_type에 대한 먹이 기록을 삭제합니다."
)
def delete_pet_feed(
    pet_id: str,
    date: date = Query(..., description="먹이 기록 날짜"),
    food_type: str = Query(..., description="음식 타입"),
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    result = pet_feed_service.delete_pet_feed_by_food_type(db, firebase_uid, pet_id, date, food_type)
    if not result:
        raise HTTPException(status_code=404, detail="Pet feed record not found")
    return None