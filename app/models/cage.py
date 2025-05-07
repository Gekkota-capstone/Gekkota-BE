from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core import Base

class Cage(Base):
    __tablename__ = "cages"  # 데이터베이스 테이블 이름

    # 기본 케이지 정보
    id = Column(Integer, primary_key=True, index=True)  # 케이지 고유 ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 소유자 ID (외래키)
    name = Column(String(255), nullable=False)  # 케이지 이름
    species = Column(String(255), nullable=False)  # 파충류 종류
    gender = Column(String(255), nullable=False)  # 파충류 성별
    birth_date = Column(String(255), nullable=False)  # 파충류 생일
    cleaning_cycle = Column(Integer, nullable=True)  # 청소 주기 (일 단위)
    state = Column(String(255), nullable=True)  # 케이지 상태
    
    # 관계 설정
    cleaning_records = relationship("CleaningRecord", back_populates="cage", cascade="all, delete-orphan")  # 청소 기록 관계
    health_records = relationship("HealthRecord", back_populates="cage", cascade="all, delete-orphan")  # 건강 기록 관계
    feeding_records = relationship("FeedingRecord", back_populates="cage", cascade="all, delete-orphan")  # 먹이 급여 기록 관계 