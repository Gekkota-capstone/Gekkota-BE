from sqlalchemy.orm import Session
from app.models.camera import CameraData

# 케이지별 카메라 데이터 조회
def get_camera_data_by_cage(db: Session, cage_id: int):
    # 케이지의 모든 카메라 데이터 조회
    records = db.query(CameraData).filter(CameraData.cage_id == cage_id).all()
    # 각 레코드의 비디오 URL 리스트 설정
    for r in records:
        r.video_url = r.get_video_urls()
    return records