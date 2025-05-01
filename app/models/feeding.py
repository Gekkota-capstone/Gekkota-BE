from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class FeedingRecord(Base):
    __tablename__ = "feeding_records"  # 데이터베이스 테이블 이름

    # 기본 먹이 급여 기록 정보
    id = Column(Integer, primary_key=True, index=True)  # 먹이 급여 기록 고유 ID
    cage_id = Column(Integer, ForeignKey("cages.id", ondelete="CASCADE"), nullable=False)  # 케이지 ID (외래키)
    feeding_date = Column(Date, nullable=False)  # 급여 날짜
    food_type = Column(String(255), nullable=False)  # 먹이 종류
    food_size = Column(String(255), nullable=False)  # 먹이 크기
    food_amount = Column(Integer, nullable=False)  # 먹이 양
    
    # 관계 설정
    cage = relationship("Cage", back_populates="feeding_records")  # 케이지와의 관계