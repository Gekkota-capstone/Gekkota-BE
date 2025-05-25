# /repository/device_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from repository.entity.device_entity import Device
import uuid


class DeviceRepository:
    def create_device(self, db: Session, data: Dict[str, Any]) -> Device:
        # Generate a unique device_id if not provided
        device_id = data.get("device_id", str(uuid.uuid4()))

        db_device = Device(
            device_id=device_id,
            SN=data.get("SN"),
            UID=data.get("UID"),
            IP=data.get("IP"),
            rtsp_url=data.get("rtsp_url")
        )
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        return db_device

    def get_by_id(self, db: Session, device_id: str) -> Optional[Device]:
        return db.query(Device).filter(Device.device_id == device_id).first()

    def get_device_by_sn(self, db: Session, sn: str) -> Optional[Device]:
        return db.query(Device).filter(Device.SN == sn).first()

    def get_by_firebase_uid(self, db: Session, firebase_uid: str) -> List[Device]:
        """Get devices associated with a specific firebase_uid"""
        return db.query(Device).filter(Device.UID == firebase_uid).all()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Device]:
        return db.query(Device).offset(skip).limit(limit).all()

    def update(self, db: Session, device_id: str, **kwargs) -> Optional[Device]:
        db_device = self.get_by_id(db, device_id)
        if db_device:
            for key, value in kwargs.items():
                setattr(db_device, key, value)
            db.commit()
            db.refresh(db_device)
        return db_device

    def update_by_sn(self, db: Session, sn: str, data: Dict[str, Any]) -> Optional[Device]:
        db_device = self.get_device_by_sn(db, sn)
        if db_device:
            # Store old IP for comparison
            old_ip = db_device.IP

            # Update fields
            for key, value in data.items():
                if hasattr(db_device, key):
                    setattr(db_device, key, value)

            # If IP is changed, automatically update rtsp_url
            new_ip = data.get("IP")
            if new_ip and new_ip != old_ip:
                db_device.rtsp_url = f"rtsp://{new_ip}:8554/stream"

            db.commit()
            db.refresh(db_device)
        return db_device

    def delete(self, db: Session, device_id: str) -> bool:
        db_device = self.get_by_id(db, device_id)
        if db_device:
            db.delete(db_device)
            db.commit()
            return True
        return False

    def count_serial_prefix(self, db: Session, prefix: str) -> int:
        return db.query(Device).filter(Device.SN.like(f"{prefix}%")).count()