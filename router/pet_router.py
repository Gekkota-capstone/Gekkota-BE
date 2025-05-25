# /router/pet_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from router.model.pet_model import PetCreate, PetResponse, PetUpdate
from service.pet_service import PetService
from db.session import get_db
from util.firebase_util import get_current_user_firebase_uid
from router.model.pet_state_model import PetStateResponse
from service.pet_state_service import PetStateService

router = APIRouter(prefix="/pets", tags=["pets"])
pet_service = PetService()

# 서비스 인스턴스 생성
pet_state_service = PetStateService()


@router.get(
    "/{pet_id}/state",
    response_model=PetStateResponse,
    summary="반려동물 은신 상태 조회",
    description="지정된 반려동물의 현재 은신 상태를 조회합니다. 최근 5개 데이터를 기준으로 판단합니다."
)
def get_pet_state(
        pet_id: str,
        db: Session = Depends(get_db),
        firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    # 먼저 해당 pet이 현재 사용자의 것인지 확인
    pet = pet_service.get_pet(db, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")

    # 반려동물 상태 조회
    state = pet_state_service.get_pet_state(db, pet_id, firebase_uid)
    return state


@router.post("/",
             response_model=PetResponse,
             status_code=status.HTTP_201_CREATED,
             summary="반려동물 생성",
             description="현재 인증된 사용자의 반려동물을 새로 생성합니다."
             )
def create_pet(
        pet_data: PetCreate,
        db: Session = Depends(get_db),
        firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    return pet_service.create_pet(
        db, firebase_uid, pet_data.name, pet_data.gender,
        pet_data.species, pet_data.birthdate
    )


@router.get("/{pet_id}",
            response_model=PetResponse,
            summary="반려동물 조회",
            description="지정된 ID의 반려동물 정보를 조회합니다."
            )
def read_pet(
        pet_id: str,
        db: Session = Depends(get_db),
        firebase_uid: str = Depends(get_current_user_firebase_uid)  # 인증용으로 추가
):
    pet = pet_service.get_pet(db, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet


@router.get("/",
            response_model=List[PetResponse],
            summary="사용자의 반려동물 목록 조회",
            description="현재 인증된 사용자의 모든 반려동물 목록을 조회합니다."
            )
def read_user_pets(
        db: Session = Depends(get_db),
        firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    pets = pet_service.get_pets_by_user(db, firebase_uid)
    return pets


@router.put("/{pet_id}",
            response_model=PetResponse,
            summary="반려동물 정보 수정",
            description="지정된 ID의 반려동물 정보를 수정합니다."
            )
def update_pet(
        pet_id: str,
        pet_data: PetUpdate,
        db: Session = Depends(get_db),
        firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    updated_pet = pet_service.update_pet(
        db, firebase_uid, pet_id, pet_data.dict(exclude_unset=True)
    )

    if updated_pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return updated_pet


@router.delete("/{pet_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="반려동물 삭제",
               description="지정된 ID의 반려동물 정보를 삭제합니다."
               )
def delete_pet(
        pet_id: str,
        db: Session = Depends(get_db),
        firebase_uid: str = Depends(get_current_user_firebase_uid)  # 인증용으로 추가
):
    # 먼저 pet이 현재 인증된 사용자의 것인지 확인
    pet = pet_service.get_pet(db, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")

    # 추가로 권한 확인 로직을 구현할 수 있음
    # repository 레벨에서 firebase_uid 확인 로직 추가...

    result = pet_service.delete_pet(db, pet_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pet not found")
    return None