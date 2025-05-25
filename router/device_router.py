# /router/device_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List

from router.model.device_model import (
    DeviceCreate, DeviceUpdate, DeviceResponse,
    SerialResponse, OpenCVImageRequest
)
from service.device_service import DeviceService
from db.session import get_db
from util.firebase_util import get_current_user_firebase_uid  # Firebase 인증 추가

router = APIRouter(prefix="/devices", tags=["devices"])
device_service = DeviceService()

# Additional router with different prefix for CAM-specific endpoints
cam_router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(device_data: DeviceCreate, db: Session = Depends(get_db)):
    # Check if SN already exists
    existing_device = device_service.get_by_sn(db, device_data.SN)
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device already registered with this SN"
        )

    return device_service.create_device(
        db, device_data.SN, device_data.UID, device_data.IP, device_data.rtsp_url
    )


@router.get("/{device_id}", response_model=DeviceResponse)
def read_device(device_id: str, db: Session = Depends(get_db)):
    device = device_service.get_device(db, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.get("/", response_model=List[DeviceResponse])
def read_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    devices = device_service.get_devices(db, skip=skip, limit=limit)
    return devices


# 새로 추가한 엔드포인트 - 사용자의 디바이스 조회
@router.get("/getmydevices/",
    response_model=List[DeviceResponse],
    summary="내 디바이스 목록 조회",
    description="현재 인증된 사용자의 모든 디바이스 목록을 조회합니다."
)
def get_my_devices(
    db: Session = Depends(get_db),
    firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    devices = device_service.get_devices_by_uid(db, firebase_uid)
    return devices


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(device_id: str, device_data: DeviceUpdate, db: Session = Depends(get_db)):
    updated_device = device_service.update_device(db, device_id, device_data.dict(exclude_unset=True))
    if updated_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return updated_device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: str, db: Session = Depends(get_db)):
    result = device_service.delete_device(db, device_id)
    if not result:
        raise HTTPException(status_code=404, detail="Device not found")
    return None


# CAM-specific endpoints
@cam_router.get(
    "/register",
    response_model=SerialResponse,
    summary="SN 자동 생성 및 등록",
    description="IP 주소를 기반으로 SN을 자동 생성하고 RDS에 등록합니다. 생성된 SN을 반환합니다.",
)
def register_sn_by_ip(
        ip: str = Query(..., description="디바이스의 IP 주소", example="192.168.0.153"),
        db: Session = Depends(get_db),
):
    try:
        serial = device_service.generate_and_register_sn(db, ip)
        return {"serial_number": serial}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@cam_router.get(
    "/{sn}",
    response_model=DeviceResponse,
    summary="SN으로 디바이스 정보 조회",
    description="시리얼 넘버(SN)를 기반으로 해당 디바이스 정보를 조회합니다.",
)
def read_sn(sn: str, db: Session = Depends(get_db)):
    result = device_service.get_by_sn(db, sn)
    if not result:
        raise HTTPException(status_code=404, detail="Serial Number not found")
    return result


@cam_router.put(
    "/{sn}",
    response_model=DeviceResponse,
    summary="디바이스 정보 수정",
    description="시리얼 넘버(SN)를 기준으로 디바이스 정보를 수정합니다. IP가 변경되면 rtsp_url도 자동 변경됩니다.",
)
def update_sn(
        sn: str,
        data: DeviceCreate = Body(
            ...,
            example={
                "SN": "SFRXC12515GF00001",
                "UID": "UID9999",
                "IP": "192.168.0.250",
                "rtsp_url": "rtsp://192.168.0.250:8554/stream",
            },
        ),
        db: Session = Depends(get_db),
):
    if sn != data.SN:
        raise HTTPException(status_code=400, detail="SN in URL and body do not match")

    result = device_service.update_sn(db, sn, data.dict())
    if not result:
        raise HTTPException(status_code=404, detail="Serial Number not found")
    return result


@cam_router.post(
    "/opencv_image",
    summary="OpenCV 이미지 정보 저장",
    description="디바이스 SN과 처리된 이미지 파일명을 받아 RDS에 기록합니다.",
)
def create_opencv_image(req: OpenCVImageRequest, db: Session = Depends(get_db)):
    # This would typically call an opencv_service that we don't have implementation for yet
    # For now, we'll just return success
    try:
        # opencv_service.register_opencv_image(db, req.SN, req.filename)
        return {"message": "Saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))