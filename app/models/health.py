from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
import json

class HealthRecord(Base):
    __tablename__ = "health_records"  # 데이터베이스 테이블 이름

    # 기본 건강 기록 정보
    id = Column(Integer, primary_key=True, index=True)  # 건강 기록 고유 ID
    cage_id = Column(Integer, ForeignKey("cages.id", ondelete="CASCADE"), nullable=False)  # 케이지 ID (외래키)
    record_date = Column(Date, nullable=False)  # 기록 날짜
    weight = Column(Float, nullable=False)  # 체중
    memo = Column(String(255), nullable=True)  # 메모
    shedding_status = Column(String(255), nullable=True)  # 탈피 상태
    photo_urls = Column(Text, nullable=True)  # 사진 URL 리스트 (JSON 문자열로 저장)

    # 관계 설정
    cage = relationship("Cage", back_populates="health_records")  # 케이지와의 관계

    # 사진 URL 리스트를 JSON 문자열에서 파싱하여 반환
    def get_photo_list(self):
        if not self.photo_urls:
            return []
        try:
            return json.loads(self.photo_urls)
        except json.JSONDecodeError:
            return []

    # 사진 URL 리스트를 JSON 문자열로 변환하여 저장
    def set_photo_list(self, photo_list):
        self.photo_urls = json.dumps(photo_list) if photo_list else None