# /service/pet_state_service.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PetStateService:
    def get_pet_state(self, db: Session, pet_id: str, firebase_uid: str) -> Dict[str, Any]:
        """
        반려동물의 현재 상태 정보 조회 (간소화된 버전)
        - 은신 여부만 판단 (최근 5개 데이터만 사용)

        Args:
            db: 데이터베이스 세션
            pet_id: 반려동물 ID
            firebase_uid: 사용자 Firebase UID

        Returns:
            Dict[str, Any]: 반려동물 상태 정보 (pet_id, is_hiding)
        """
        # 기기 정보 조회 (pet_id로 기기의 SN 가져오기)
        device_sn = self._get_device_sn_for_pet(db, pet_id)
        if not device_sn:
            device_sn = "SFRXC12515GF00001"  # 기본값 설정
            logger.warning(f"No device found for pet {pet_id}, using default: {device_sn}")

        # 은신 상태 판단 (최근 5개 데이터만 사용)
        is_hiding = self._analyze_hiding_behavior(db, device_sn)

        # 결과 구성 (간소화)
        return {
            "pet_id": pet_id,
            "is_hiding": is_hiding
        }

    def _get_device_sn_for_pet(self, db: Session, pet_id: str) -> Optional[str]:
        """펫 ID에 해당하는 기기 SN 조회"""
        try:
            # 여기서는 간단하게 하드코딩된 값을 반환
            # 실제로는 DB에서 pet과 device 간의 관계를 조회해야 함
            return "SFRXC12515GF00001"
        except Exception as e:
            logger.error(f"Error getting device SN for pet {pet_id}: {e}")
            return None

    def _analyze_hiding_behavior(self, db: Session, device_sn: str) -> bool:
        """
        은신 행동 분석 (간소화된 버전)
        - 최근 5개 YOLO 데이터만 분석하여 은신 여부 판단

        Returns:
            bool: 은신 여부
        """
        try:
            # 최근 5개 YOLO 결과 조회
            query = text(f"""
                SELECT yolo_result 
                FROM capstone.yolo_results 
                WHERE device = :device_sn
                ORDER BY yolo_result->>'timestamp' DESC
                LIMIT 5
            """)

            # 쿼리 실행
            results = db.execute(query, {"device_sn": device_sn})

            # 결과 변환
            data = [row[0] for row in results]

            # 데이터가 없으면 은신 아님으로 판단
            if not data:
                return False

            # 은신 판단 기준
            # 1. 5개 중 2개 이상 박스가 없으면 은신으로 판단
            # 2. 키포인트 신뢰도가 낮은 경우 (6개 이상 저신뢰도) 은신으로 판단
            no_box_count = 0
            low_keypoint_frames = 0

            for yolo_data in data:
                boxes = yolo_data.get("boxes", [])

                # 박스 없음 체크
                if not boxes:
                    no_box_count += 1
                    continue

                # 키포인트 신뢰도 체크
                keypoints_list = yolo_data.get("keypoints", [[]])[0] if yolo_data.get("keypoints") else []

                if keypoints_list:
                    low_conf_kpts = [
                        kp for kp in keypoints_list
                        if kp.get("conf", 0) <= 0.3
                    ]

                    if len(low_conf_kpts) >= 6:
                        low_keypoint_frames += 1

            # 판단 결과 반환
            return no_box_count >= 2 or low_keypoint_frames >= 2

        except Exception as e:
            logger.error(f"Error analyzing hiding behavior for device {device_sn}: {e}")
            return False