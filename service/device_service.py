# /service/device_service.py

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from repository.device_repository import DeviceRepository
import uuid
from datetime import datetime


class DeviceService:
    def __init__(self):
        self.repository = DeviceRepository()

    def create_device(self, db: Session, SN: str, UID: Optional[str] = None,
                      IP: Optional[str] = None, rtsp_url: Optional[str] = None) -> Dict[str, Any]:
        # Generate a unique device_id
        device_id = str(uuid.uuid4())

        # Create data dictionary
        data = {
            "device_id": device_id,
            "SN": SN,
            "UID": UID,
            "IP": IP,
            "rtsp_url": rtsp_url
        }

        device = self.repository.create_device(db, data)
        return self._device_to_dict(device)

    # 추가된 메소드 - 사용자의 디바이스 목록 조회
    def get_devices_by_uid(self, db: Session, firebase_uid: str) -> List[Dict[str, Any]]:
        """
        사용자의 firebase_uid와 일치하는 UID를 가진 디바이스 목록을 반환합니다.

        Args:
            db: 데이터베이스 세션
            firebase_uid: 사용자의 Firebase UID

        Returns:
            List[Dict[str, Any]]: 디바이스 목록
        """
        devices = self.repository.get_by_firebase_uid(db, firebase_uid)
        return [self._device_to_dict(device) for device in devices]

    def generate_and_register_sn(self, db: Session, ip: str) -> str:
        if not ip:
            raise ValueError("IP is required")

        # 시리얼 넘버 구성 요소
        manufacturer = "SF"
        model = "RXC1"
        now = datetime.utcnow()
        year = str(now.year % 100).zfill(2)
        week = str(now.isocalendar()[1]).zfill(2)  # Compatible with Python 3.8+ (isocalendar returns a tuple)
        factory = "GF"

        # SN prefix 기반 개수 → 시퀀스 생성
        base_prefix = f"{manufacturer}{model}{year}{week}{factory}"
        existing_count = self.repository.count_serial_prefix(db, base_prefix)
        seq_num = str(existing_count + 1).zfill(5)
        final_sn = f"{base_prefix}{seq_num}"

        # rtsp_url 구성
        rtsp_url = f"rtsp://{ip}:8554/stream"

        # DB 저장
        device_data = {
            "device_id": str(uuid.uuid4()),
            "SN": final_sn,
            "IP": ip,
            "rtsp_url": rtsp_url
        }
        device = self.repository.create_device(db, device_data)
        return final_sn

    def get_device(self, db: Session, device_id: str) -> Optional[Dict[str, Any]]:
        device = self.repository.get_by_id(db, device_id)
        if not device:
            return None
        return self._device_to_dict(device)

    def get_by_sn(self, db: Session, sn: str) -> Optional[Dict[str, Any]]:
        device = self.repository.get_device_by_sn(db, sn)
        if not device:
            return None
        return self._device_to_dict(device)

    def get_devices(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        devices = self.repository.get_all(db, skip, limit)
        return [self._device_to_dict(device) for device in devices]

    def update_device(self, db: Session, device_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        device = self.repository.update(db, device_id, **data)
        if not device:
            return None
        return self._device_to_dict(device)

    def update_sn(self, db: Session, sn: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        device = self.repository.update_by_sn(db, sn, data)
        if not device:
            return None
        return self._device_to_dict(device)

    def delete_device(self, db: Session, device_id: str) -> bool:
        return self.repository.delete(db, device_id)

    def _device_to_dict(self, device) -> Dict[str, Any]:
        return {
            "device_id": device.device_id,
            "SN": device.SN,
            "UID": device.UID,
            "IP": device.IP,
            "rtsp_url": device.rtsp_url
        }