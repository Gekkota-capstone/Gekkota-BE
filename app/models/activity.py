from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey
from app.database import Base

class ActivityData(Base):
    __tablename__ = "activity_data"  # 데이터베이스 테이블 이름

    # 기본 활동 데이터 정보
    id = Column(Integer, primary_key=True, index=True)  # 활동 데이터 고유 ID
    camera_data_id = Column(Integer, ForeignKey("camera_data.id"), nullable=False)  # 카메라 데이터 ID (외래키)
    timestamp = Column(DateTime, nullable=False)  # 활동 시간
    activity_level = Column(Float, nullable=False)  # 활동 수준 (0.0 ~ 1.0)