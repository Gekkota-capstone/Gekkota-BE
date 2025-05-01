from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.notification import NotificationUpdate

# 사용자의 알림 설정 업데이트
def update_user_notifications(db: Session, user_id: int, settings: NotificationUpdate):
    # 사용자 조회
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # 알림 설정 업데이트
    user.care_notification = settings.care  # 케어 알림 설정
    user.event_notification = settings.event  # 이벤트 알림 설정
    user.service_notification = settings.service  # 서비스 알림 설정
    
    db.commit()
    db.refresh(user)
    return user

# 사용자의 알림 설정 조회
def get_user_notifications(db: Session, user_id: int):
    # 사용자 조회
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # 알림 설정 반환
    return {
        "care": user.care_notification,  # 케어 알림 상태
        "event": user.event_notification,  # 이벤트 알림 상태
        "service": user.service_notification  # 서비스 알림 상태
    }