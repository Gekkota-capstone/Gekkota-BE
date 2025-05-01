from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CleaningRecord(Base):
    __tablename__ = "cleaning_records"  # 데이터베이스 테이블 이름

    # 기본 청소 기록 정보
    id = Column(Integer, primary_key=True, index=True)  # 청소 기록 고유 ID
    cage_id = Column(Integer, ForeignKey("cages.id", ondelete="CASCADE"), nullable=False)  # 케이지 ID (외래키)
    cleaning_date = Column(Date, nullable=False)  # 청소 날짜
    
    # 관계 설정
    cage = relationship("Cage", back_populates="cleaning_records")  # 케이지와의 관계