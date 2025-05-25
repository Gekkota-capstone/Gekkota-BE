# /repository/entity/device_entity.py

from sqlalchemy import Column, String
from db.database import Base

class Device(Base):
    __tablename__ = "device"
    __table_args__ = {"schema": "capstone"}

    device_id = Column(String, primary_key=True, index=True)
    SN = Column(String, nullable=True, unique=True)
    UID = Column(String, nullable=True)
    IP = Column(String, nullable=True)
    rtsp_url = Column(String, nullable=True)