from sqlalchemy import Column, Integer, Date, ForeignKey, Text
from app.core import Base
import json

class CameraData(Base):
    __tablename__ = "camera_data"  # 데이터베이스 테이블 이름

    # 기본 카메라 데이터 정보
    id = Column(Integer, primary_key=True, index=True)  # 카메라 데이터 고유 ID
    cage_id = Column(Integer, ForeignKey("cages.id"), nullable=False)  # 케이지 ID (외래키)
    record_date = Column(Date, nullable=False)  # 기록 날짜
    video_url = Column(Text)  # 비디오 URL 리스트 (JSON 문자열로 저장)

    # 비디오 URL 리스트를 JSON 문자열에서 파싱하여 반환
    def get_video_urls(self):
        return json.loads(self.video_url) if self.video_url else []

    # 비디오 URL 리스트를 JSON 문자열로 변환하여 저장
    def set_video_urls(self, urls):
        self.video_url = json.dumps(urls)