from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserUpdate, UserOut
from app.crud import user as user_crud
from app.database import SessionLocal
from app.auth.dependencies import get_current_user

# 사용자 관련 라우터 생성 (prefix: /users, 태그: users)
router = APIRouter(prefix="/users", tags=["users"])

# 데이터베이스 세션 의존성 함수
def get_db():
    # 새로운 데이터베이스 세션 생성
    db = SessionLocal()
    try:
        # 세션을 yield하여 라우터에서 사용할 수 있게 함
        yield db
    finally:
        # 요청 처리가 끝나면 세션을 닫음
        db.close()

# 닉네임 변경 엔드포인트 (PATCH /users/me/nickname)
@router.patch("/me/nickname", response_model=UserOut)
def change_nickname(
    update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    # 현재 사용자의 닉네임 업데이트
    user = user_crud.update_nickname(db, current_user.id, update.nickname)
    # 닉네임이 이미 존재하는 경우 에러 반환
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="닉네임 변경 실패: 이미 존재하는 닉네임입니다"
        )
    # 업데이트된 사용자 정보 반환
    return user