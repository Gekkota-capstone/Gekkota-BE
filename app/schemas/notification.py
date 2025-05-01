from pydantic import BaseModel

# 알림 설정 업데이트 요청 스키마
class NotificationUpdate(BaseModel):
    care: bool  # 케어 알림 설정
    event: bool  # 이벤트 알림 설정
    service: bool  # 서비스 알림 설정

# 알림 설정 응답 스키마
class NotificationOut(NotificationUpdate):
    pass