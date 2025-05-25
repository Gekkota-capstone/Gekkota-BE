# /router/pet_clean_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from router.model.pet_clean_model import PetCleanCreate, PetCleanUpdate, PetCleanResponse
from service.pet_clean_service import PetCleanService
from db.session import get_db
from util.firebase_util import get_current_user_firebase_uid

router = APIRouter(prefix="/pet-cleans", tags=["pet-cleans"])
pet_clean_service = PetCleanService()


@router.post(
    "/{pet_id}",
    response_model=PetCleanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="반려동물 청결 기록 생성",
    description="지정된 반려동물 ID에 대한 청결 기록을 생성합니다."
)
def create_pet_clean(
    pet_id: str,
    pet_clean_data: PetCleanCreate,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    existing_pet_clean = pet_clean_service.get_pet_clean(
        db, firebase_uid, pet_id, pet_clean_data.date
    )

    if existing_pet_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pet clean record already exists for this date"
        )

    return pet_clean_service.create_pet_clean(
        db, firebase_uid, pet_id, pet_clean_data.date, pet_clean_data.memo
    )


@router.get(
    "/{pet_id}",
    response_model=PetCleanResponse,
    summary="반려동물 청결 기록 조회",
    description="지정된 반려동물 ID와 날짜에 대한 청결 기록을 조회합니다."
)
def read_pet_clean(
    pet_id: str,
    clean_date: date,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    pet_clean = pet_clean_service.get_pet_clean(db, firebase_uid, pet_id, clean_date)
    if pet_clean is None:
        return {
            "pet_id": pet_id,
            "date": clean_date,
            "memo": None
        }
    return pet_clean


@router.get(
    "/{pet_id}/date-range",
    response_model=List[PetCleanResponse],
    summary="날짜 범위로 반려동물 청결 기록 조회",
    description="지정된 반려동물 ID와 날짜 범위에 대한 청결 기록을 조회합니다."
)
def read_pet_cleans_by_date_range(
    pet_id: str,
    start_date: date = Query(..., description="시작 날짜"),
    end_date: date = Query(..., description="종료 날짜"),
    db: Session = Depends(get_db)
):
    pet_cleans = pet_clean_service.get_pet_cleans_by_date_range(db, pet_id, start_date, end_date)
    return pet_cleans


@router.put(
    "/{pet_id}",
    response_model=PetCleanResponse,
    summary="반려동물 청결 기록 수정",
    description="지정된 반려동물 ID와 날짜에 대한 청결 기록을 수정합니다."
)
def update_pet_clean(
    pet_id: str,
    pet_clean_data: PetCleanUpdate,
    date: date = Query(..., description="청결 기록 날짜"),
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    updated_pet_clean = pet_clean_service.update_pet_clean(
        db, firebase_uid, pet_id, date, pet_clean_data.dict(exclude_unset=True)
    )

    if updated_pet_clean is None:
        return {
            "pet_id": pet_id,
            "date": date,
            "memo": None
        }
    return updated_pet_clean


@router.delete(
    "/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="반려동물 청결 기록 삭제",
    description="지정된 반려동물 ID와 날짜에 대한 청결 기록을 삭제합니다."
)
def delete_pet_clean(
    pet_id: str,
    clean_date: date,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    result = pet_clean_service.delete_pet_clean(db, firebase_uid, pet_id, clean_date)
    if not result:
        raise HTTPException(status_code=404, detail="Pet clean record not found")
    return None