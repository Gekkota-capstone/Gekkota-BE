from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"  # 데이터베이스 테이블 이름

    # 기본 사용자 정보
    id = Column(Integer, primary_key=True, index=True)  # 사용자 고유 ID
    email = Column(String(255), unique=True, index=True)  # 이메일 주소 (고유값)
    name = Column(String(255))  # 사용자 이름
    nickname = Column(String(255), unique=True)  # 사용자 닉네임 (고유값)
    google_token = Column(String(255), unique=True, nullable=True)  # Google OAuth 토큰
    is_active = Column(Boolean, default=True)  # 계정 활성화 상태

    # 알림 설정
    care_notification = Column(Boolean, default=True)  # 케어 관련 알림 설정
    event_notification = Column(Boolean, default=True)  # 이벤트 관련 알림 설정
    service_notification = Column(Boolean, default=True)  # 서비스 관련 알림 설정