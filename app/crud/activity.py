from sqlalchemy.orm import Session
from app.models.activity import ActivityData

# 카메라 ID로 활동 기록 조회
def get_activity_by_camera_id(db: Session, camera_data_id: int):
    return db.query(ActivityData).filter(ActivityData.camera_data_id == camera_data_id).all()