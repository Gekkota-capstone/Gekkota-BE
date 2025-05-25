# /router/pet_health_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from router.model.pet_health_model import PetHealthCreate, PetHealthUpdate, PetHealthResponse
from service.pet_health_service import PetHealthService
from db.session import get_db
from util.firebase_util import get_current_user_firebase_uid

router = APIRouter(prefix="/pet-healths", tags=["pet-healths"])
pet_health_service = PetHealthService()


@router.post(
    "/{pet_id}",
    response_model=PetHealthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="반려동물 건강 기록 생성",
    description="지정된 반려동물 ID에 대한 건강 기록을 생성합니다."
)
def create_pet_health(
    pet_id: str,
    pet_health_data: PetHealthCreate,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    existing_pet_health = pet_health_service.get_pet_health(
        db, firebase_uid, pet_id, pet_health_data.date
    )

    # 값이 있는지 확인하는 방법 변경 필요 (None이 반환되지 않으므로)
    if existing_pet_health.get("weight") is not None or existing_pet_health.get("memo") is not None or existing_pet_health.get("shedding_status") is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pet health record already exists for this date"
        )

    return pet_health_service.create_pet_health(
        db, firebase_uid, pet_id,
        pet_health_data.date, pet_health_data.weight, pet_health_data.memo,
        pet_health_data.shedding_status
    )


@router.get(
    "/{pet_id}",
    response_model=PetHealthResponse,
    summary="반려동물 건강 기록 조회",
    description="지정된 반려동물 ID와 날짜에 대한 건강 기록을 조회합니다. 월간 및 연간 체중 통계가 포함됩니다."
)
def read_pet_health(
    pet_id: str,
    date: date = Query(..., description="건강 기록 날짜"),
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    # 레코드가 없는 경우에도 기본 구조 반환
    return pet_health_service.get_pet_health(db, firebase_uid, pet_id, date)


@router.get(
    "/{pet_id}/date-range",
    response_model=List[PetHealthResponse],
    summary="날짜 범위로 반려동물 건강 기록 조회",
    description="지정된 반려동물 ID와 날짜 범위에 대한 건강 기록을 조회합니다."
)
def read_pet_healths_by_date_range(
    pet_id: str,
    start_date: date = Query(..., description="시작 날짜"),
    end_date: date = Query(..., description="종료 날짜"),
    db: Session = Depends(get_db)
):
    pet_healths = pet_health_service.get_pet_healths_by_date_range(db, pet_id, start_date, end_date)
    return pet_healths


@router.put(
    "/{pet_id}",
    response_model=PetHealthResponse,
    summary="반려동물 건강 기록 수정",
    description="지정된 반려동물 ID와 날짜에 대한 건강 기록을 수정합니다."
)
def update_pet_health(
    pet_id: str,
    pet_health_data: PetHealthUpdate,
    date: date = Query(..., description="건강 기록 날짜"),
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    updated_pet_health = pet_health_service.update_pet_health(
        db, firebase_uid, pet_id, date, pet_health_data.dict(exclude_unset=True)
    )

    if updated_pet_health is None:
        raise HTTPException(status_code=404, detail="Pet health record not found")
    return updated_pet_health


@router.delete(
    "/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="반려동물 건강 기록 삭제",
    description="지정된 반려동물 ID와 날짜에 대한 건강 기록을 삭제합니다."
)
def delete_pet_health(
    pet_id: str,
    date: date = Query(..., description="건강 기록 날짜"),
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    result = pet_health_service.delete_pet_health(db, firebase_uid, pet_id, date)
    if not result:
        raise HTTPException(status_code=404, detail="Pet health record not found")
    return None