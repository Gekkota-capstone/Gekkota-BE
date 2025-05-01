from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.notification import NotificationUpdate, NotificationOut
from app.crud import notification as notification_crud
from app.auth.dependencies import get_current_user
from app.schemas.user import UserOut

# 알림 설정 관련 라우터 생성 (prefix: /users/me/notifications, 태그: notifications)
router = APIRouter(prefix="/users/me/notifications", tags=["notifications"])

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

# 알림 설정 업데이트 엔드포인트 (PATCH /users/me/notifications)
@router.patch("", response_model=NotificationOut)
def update_notifications(
    settings: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    # 현재 사용자의 알림 설정 업데이트
    updated = notification_crud.update_user_notifications(db, current_user.id, settings)
    # 사용자가 존재하지 않는 경우 에러 반환
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    # 업데이트된 알림 설정 반환
    return settings

# 알림 설정 조회 엔드포인트 (GET /users/me/notifications)
@router.get("", response_model=NotificationOut)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    # 현재 사용자의 알림 설정 조회
    data = notification_crud.get_user_notifications(db, current_user.id)
    # 사용자가 존재하지 않는 경우 에러 반환
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    # 알림 설정 반환
    return data