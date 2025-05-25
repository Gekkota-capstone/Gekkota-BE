# /service/rtsp_service.py

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from repository.device_repository import DeviceRepository


class RtspService:
    def __init__(self):
        self.device_repository = DeviceRepository()

    def get_rtsp_url_by_firebase_uid(self, db: Session, firebase_uid: str) -> Dict[str, Any]:
        """
        Firebase UID에 해당하는 사용자의 디바이스 RTSP URL을 조회합니다.

        Args:
            db: 데이터베이스 세션
            firebase_uid: 조회할 사용자의 Firebase UID

        Returns:
            RTSP URL 정보를 포함한 딕셔너리
        """
        # 사용자와 연결된 디바이스 목록 조회
        devices = self.device_repository.get_by_firebase_uid(db, firebase_uid)

        # 첫 번째 디바이스의 RTSP URL 반환
        # 여러 디바이스가 있는 경우 첫 번째 디바이스의 URL만 반환
        rtsp_url = None
        if devices and len(devices) > 0:
            rtsp_url = devices[0].rtsp_url

        # 응답 형식 준비
        return {
            "rtsp_url": rtsp_url or ""  # URL이 없는 경우 빈 문자열 반환
        }