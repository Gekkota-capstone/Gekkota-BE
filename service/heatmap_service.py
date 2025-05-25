# /service/heatmap_service.py

from sqlalchemy.orm import Session
import logging
import os
from datetime import datetime, timedelta
from util.heatmap_generator import (
    fetch_yolo_data,
    generate_heatmap,
    upload_to_s3,
    connect_to_s3,
    cleanup_temp_files,
    get_kst_now,
    DEVICE_SN
)

logger = logging.getLogger(__name__)


class HeatmapService:
    """히트맵 생성 및 관리 서비스"""

    def generate_and_upload_heatmap(self, session: Session, date_str: str = None, device_serial: str = None) -> dict:
        """
        히트맵 생성 및 S3 업로드

        Args:
            session: 데이터베이스 세션
            date_str: 날짜 문자열 (YYYYMMDD 형식, None이면 어제 날짜를 사용)
            device_serial: 장치 시리얼 번호 (None이면 기본값 사용)

        Returns:
            dict: 처리 결과 및 URL 정보
        """
        heatmap_path = None

        try:
            # 날짜와 장치 기본값 설정
            if not date_str:
                # 날짜를 지정하지 않으면 어제 날짜 사용
                date_str = (get_kst_now() - timedelta(days=1)).strftime("%Y%m%d")
                logger.info(f"날짜를 지정하지 않아 어제 날짜({date_str})를 사용합니다.")
            else:
                logger.info(f"지정된 날짜: {date_str}")

            if not device_serial:
                device_serial = DEVICE_SN
                logger.info(f"장치를 지정하지 않아 기본 장치({device_serial})를 사용합니다.")

            # 날짜 형식 검증
            if len(date_str) != 8 or not date_str.isdigit():
                return {
                    "success": False,
                    "message": "날짜 형식이 올바르지 않습니다. YYYYMMDD 형식이어야 합니다.",
                    "url": None
                }

            # 날짜 문자열 -> 날짜 객체 변환 (검증용)
            try:
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                logger.info(f"디바이스 {device_serial}의 {formatted_date} 데이터로 히트맵 생성 시작")
            except ValueError:
                return {
                    "success": False,
                    "message": "유효하지 않은 날짜입니다.",
                    "url": None
                }

            # YOLO 데이터 가져오기
            yolo_results = fetch_yolo_data(session, device_serial, date_str)

            if not yolo_results:
                return {
                    "success": False,
                    "message": f"해당 날짜({date_str})에 YOLO 데이터가 없습니다.",
                    "url": None
                }

            # 히트맵 생성
            heatmap_path = generate_heatmap(yolo_results)

            if not heatmap_path:
                return {
                    "success": False,
                    "message": "히트맵 생성에 실패했습니다.",
                    "url": None
                }

            # S3 업로드
            s3_client, bucket = connect_to_s3()

            if not s3_client or not bucket:
                return {
                    "success": False,
                    "message": "S3 연결에 실패했습니다.",
                    "url": None
                }

            # S3 키 설정
            s3_key = f"heatmap/{date_str}/{device_serial}_heatmap.png"

            # S3 업로드
            success, s3_url = upload_to_s3(s3_client, bucket, heatmap_path, s3_key)

            if not success:
                return {
                    "success": False,
                    "message": "S3 업로드에 실패했습니다.",
                    "url": None
                }

            logger.info(f"히트맵 생성 및 업로드 완료: {s3_url}")

            return {
                "success": True,
                "message": "히트맵 생성 및 업로드에 성공했습니다.",
                "url": s3_url,
                "date": date_str,
                "device_serial": device_serial
            }

        except Exception as e:
            logger.error(f"히트맵 처리 오류: {str(e)}")
            return {
                "success": False,
                "message": f"처리 중 오류가 발생했습니다: {str(e)}",
                "url": None
            }
        finally:
            # 임시 파일 정리
            if heatmap_path:
                cleanup_temp_files(heatmap_path)

    def generate_previous_day_heatmap(self, session: Session, device_serial: str = None) -> dict:
        """
        전날 데이터로 히트맵 생성

        Args:
            session: 데이터베이스 세션
            device_serial: 장치 시리얼 번호 (None이면 기본값 사용)

        Returns:
            dict: 처리 결과 및 URL 정보
        """
        # 전날 날짜 계산
        yesterday = (get_kst_now() - timedelta(days=1)).strftime("%Y%m%d")
        logger.info(f"전날({yesterday}) 데이터로 히트맵 생성 시작")
        return self.generate_and_upload_heatmap(session, yesterday, device_serial)