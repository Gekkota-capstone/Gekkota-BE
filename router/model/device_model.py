# /router/model/device_model.py

from pydantic import BaseModel, Field
from typing import Optional


class DeviceBase(BaseModel):
    SN: str = Field(..., example="SFRXC12515GF00001")
    UID: Optional[str] = Field(None, example="UID123456")
    IP: Optional[str] = Field(None, example="192.168.0.200")
    rtsp_url: Optional[str] = Field(None, example="rtsp://192.168.0.200:8554/stream")


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    UID: Optional[str] = Field(None, example="UID123456")
    IP: Optional[str] = Field(None, example="192.168.0.200")
    rtsp_url: Optional[str] = Field(None, example="rtsp://192.168.0.200:8554/stream")


class DeviceResponse(DeviceBase):
    device_id: str

    class Config:
        orm_mode = True


class SerialResponse(BaseModel):
    serial_number: str = Field(..., example="SFRXC12515GF00001")


class OpenCVImageRequest(BaseModel):
    SN: str = Field(..., example="SFRXC12515GF00001")
    filename: str = Field(..., example="SFRXC12515GF00001_20250413_140000.jpg")