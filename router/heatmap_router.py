# /router/heatmap_router.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from service.heatmap_service import HeatmapService
from db.session import get_db
from util.firebase_util import get_current_user_firebase_uid
from util.heatmap_generator import get_kst_now


# 응답 모델 정의
class HeatmapResponse(BaseModel):
    success: bool
    message: str
    url: Optional[str] = None
    date: Optional[str] = None
    target_date: Optional[str] = None  # 실제 처리된 날짜 (하루 전)
    device_serial: Optional[str] = None


# 라우터 생성
router = APIRouter(prefix="/heatmaps", tags=["heatmaps"])
heatmap_service = HeatmapService()


@router.get(
    "/generate",
    response_model=HeatmapResponse,
    summary="히트맵 생성",
    description="지정된 날짜의 **전날** 데이터로 히트맵을 생성하고 S3에 업로드합니다. 날짜를 지정하지 않으면 어제 날짜를 사용합니다."
)
def generate_heatmap(
        date: Optional[str] = Query(None, description="기준 날짜 (YYYYMMDD 형식, 지정된 날짜의 전날 데이터가 사용됨)"),
        db: Session = Depends(get_db),
        firebase_uid: str = Depends(get_current_user_firebase_uid)
):
    """히트맵 생성 및 S3 업로드 엔드포인트"""
    # 날짜 처리 로직
    if date:
        # 날짜 형식 검증
        if len(date) != 8 or not date.isdigit():
            raise HTTPException(
                status_code=400,
                detail="날짜 형식이 올바르지 않습니다. YYYYMMDD 형식이어야 합니다."
            )
        try:
            # 입력된 날짜에서 하루 전 날짜 계산
            input_date = datetime.strptime(date, "%Y%m%d")
            target_date = (input_date - timedelta(days=1)).strftime("%Y%m%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="유효하지 않은 날짜입니다."
            )
    else:
        # 날짜를 지정하지 않으면 어제 날짜 사용
        target_date = (get_kst_now() - timedelta(days=1)).strftime("%Y%m%d")
        date = get_kst_now().strftime("%Y%m%d")  # 오늘 날짜 (기준점)

    # 히트맵 생성
    result = heatmap_service.generate_and_upload_heatmap(db, target_date)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    # 응답에 원본 기준 날짜와 실제 처리 날짜 모두 포함
    result["date"] = date
    result["target_date"] = target_date

    return result