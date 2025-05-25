# /router/s3_router.py

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from db.session import get_db
from service import s3_service
from typing import List, Optional

# Create two routers with different prefixes
router = APIRouter(prefix="/s3", tags=["s3"])
cam_router = APIRouter(prefix="/s3", tags=["s3-cam"])

class UploadRequest(BaseModel):
    SN: str = Field(..., example="SFRXC12515GF00001")
    filename: str = Field(..., example="SFRXC12515GF00001_20250413_140000.mp4")

class UploadResponse(BaseModel):
    upload_url: str = Field(
        ...,
        example="https://direp.s3.ap-northeast-2.amazonaws.com/stream/SFRXC12515GF00001/20250413/SFRXC12515GF00001_20250413_140000.mp4?...",
    )
    s3_key: str = Field(
        ...,
        example="stream/SFRXC1251x5GF00001/20250413/SFRXC12515GF00001_20250413_140000.mp4",
    )
    expires_in: int = Field(..., example=300)

class VideoFile(BaseModel):
    filename: str = Field(..., example="SFRXC12515GF00001_20250508_002000.mp4")
    download_url: str = Field(..., example="https://direp.s3.ap-northeast-2.amazonaws.com/stream/SFRXC12515GF00001/20250508/SFRXC12515GF00001_20250508_002000.mp4?...")
    s3_key: str = Field(..., example="stream/SFRXC12515GF00001/20250508/SFRXC12515GF00001_20250508_002000.mp4")
    size: int = Field(..., example=10485760)
    last_modified: str = Field(..., example="2025-05-08T00:20:30+00:00")
    content_type: str = Field(..., example="video/mp4")
    expires_in: int = Field(..., example=3600)
    time: Optional[str] = Field(None, example="002000")

class VideoListResponse(BaseModel):
    videos: List[VideoFile]

# CAM-specific endpoints
@cam_router.post(
    "/stream/upload-url",
    response_model=UploadResponse,
    summary="Stream 영상 업로드용 Pre-signed URL 발급",
    description="1분 단위 영상 파일을 S3의 stream 폴더에 업로드할 수 있도록 Pre-signed URL을 발급합니다.",
)
def get_stream_upload_url(
    req: UploadRequest = Body(
        ...,
        example={
            "SN": "SFRXC12515GF00001",
            "filename": "SFRXC12515GF00001_20250413_140000.mp4",
        },
    ),
    db: Session = Depends(get_db),
):
    try:
        return s3_service.generate_presigned_upload_url(
            db, req.SN, req.filename, folder="stream"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@cam_router.post(
    "/opencv/upload-url",
    response_model=UploadResponse,
    summary="OpenCV ZIP 업로드 presigned URL 발급",
    description="OpenCV 처리된 이미지들을 압축한 zip 파일을 S3의 opencv 폴더에 업로드할 수 있도록 presigned URL을 발급합니다.",
)
def get_opencv_upload_url(
    req: UploadRequest = Body(
        ...,
        example={
            "SN": "SFRXC12515GF00001",
            "filename": "SFRXC12515GF00001_20250413_150000.zip",
        },
    ),
    db: Session = Depends(get_db),
):
    try:
        return s3_service.generate_presigned_upload_url(
            db, req.SN, req.filename, folder="opencv"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Regular S3 endpoints for application
@router.get(
    "/video",
    response_model=VideoFile,
    summary="특정 영상 재생용 Pre-signed URL 발급",
    description="디바이스의 SN, 사용자 ID, 날짜, 시간을 기준으로 특정 영상의 재생 URL을 발급합니다.",
)
def get_video_url(
    sn: str = Query(..., description="디바이스의 시리얼 넘버", example="SFRXC12515GF00001"),
    firebase_uid: str = Query(..., description="사용자의 Firebase UID", example="uid123456"),
    date: str = Query(..., description="영상 날짜 (YYYYMMDD 또는 YYYY-MM-DD)", example="20250508"),
    time: str = Query(..., description="영상 시간 (HHMMSS 또는 HH:MM:SS)", example="002000"),
    db: Session = Depends(get_db),
):
    try:
        video = s3_service.generate_video_presigned_url(
            db, sn, firebase_uid, date, time
        )
        return video
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/videos/date",
    response_model=VideoListResponse,
    summary="특정 날짜의 영상 목록 및 URL 발급",
    description="디바이스의 SN, 사용자 ID, 날짜를 기준으로 해당 날짜의 모든 영상 목록과 재생 URL을 발급합니다.",
)
def list_videos_by_date(
    sn: str = Query(..., description="디바이스의 시리얼 넘버", example="SFRXC12515GF00001"),
    firebase_uid: str = Query(..., description="사용자의 Firebase UID", example="uid123456"),
    date: str = Query(..., description="영상 날짜 (YYYYMMDD 또는 YYYY-MM-DD)", example="20250508"),
    db: Session = Depends(get_db),
):
    try:
        videos = s3_service.list_videos_by_date(
            db, sn, firebase_uid, date
        )
        return {"videos": videos}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))