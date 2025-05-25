# /router/user_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from router.model.user_model import UserCreate, UserUpdate, UserResponse
from service.user_service import UserService
from db.session import get_db
from util.firebase_util import get_current_user_firebase_uid

router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="사용자 생성",
    description="새로운 사용자를 생성합니다. 인증된 사용자의 Firebase UID를 사용하여 생성됩니다."
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    existing_user = user_service.get_user(db, firebase_uid)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered"
        )

    return user_service.create_user(
        db, firebase_uid, user_data.nickname, user_data.profile
    )


@router.get(
    "/",
    response_model=UserResponse,
    summary="현재 사용자 정보 조회",
    description="현재 인증된 사용자의 정보를 조회합니다."
)
def read_user(
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    user = user_service.get_user(db, firebase_uid)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put(
    "/",
    response_model=UserResponse,
    summary="사용자 프로필 업데이트",
    description="현재 인증된 사용자의 프로필 정보를 업데이트합니다."
)
def update_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    updated_user = user_service.update_user(db, firebase_uid, user_data.dict(exclude_unset=True))
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="사용자 삭제",
    description="현재 인증된 사용자의 계정과 관련된 모든 데이터를 삭제합니다."
)
def delete_user(
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    result = user_service.delete_user(db, firebase_uid)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return None