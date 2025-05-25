# /router/rtsp_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from router.model.rtsp_model import RtspResponse
from service.rtsp_service import RtspService
from db.session import get_db
from util.firebase_util import get_current_user_firebase_uid

router = APIRouter(prefix="/rtsp", tags=["rtsp"])
rtsp_service = RtspService()


@router.get(
    "",
    response_model=RtspResponse,
    summary="RTSP URL 조회",
    description="현재 로그인한 사용자의 디바이스 RTSP URL을 조회합니다."
)
def get_rtsp_url(
        db: Session = Depends(get_db),
        firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    """
    현재 로그인한 사용자의 디바이스 RTSP URL을 조회합니다.

    Returns:
        사용자와 연결된 디바이스의 RTSP URL
    """
    rtsp_data = rtsp_service.get_rtsp_url_by_firebase_uid(db, firebase_uid)
    return rtsp_data