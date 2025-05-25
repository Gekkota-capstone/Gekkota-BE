# /service/pet_active_service.py

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Dict, Any, Optional, List
from repository.pet_active_repository import PetActiveRepository
from datetime import datetime, date, timedelta
import logging
from pytz import timezone
from db.s3_utils import generate_presigned_url  # S3 유틸 가져오기
from collections import Counter

# 로깅 설정
logger = logging.getLogger(__name__)

# 한국 시간대 설정
KST = timezone('Asia/Seoul')


class PetActiveService:
    def __init__(self):
        self.repository = PetActiveRepository()

    def get_pet_active(self, db: Session, firebase_uid: str, pet_id: str, query_date: Optional[date] = None) -> Dict[
        str, Any]:
        """
        반려동물의 활동 정보를 조회합니다.

        Args:
            db: 데이터베이스 세션
            firebase_uid: 사용자 Firebase UID
            pet_id: 반려동물 ID
            query_date: 조회 날짜 (None이면 현재 날짜 사용)

        Returns:
            Dict[str, Any]: 반려동물 활동 정보
        """
        # 조회 날짜 설정 (None이면 현재 날짜 사용)
        if query_date is None:
            query_date = datetime.now(KST).date()

        # 조회 날짜 문자열 변환 (YYYYMMDD 형식)
        date_str = query_date.strftime("%Y%m%d")

        # 기본 디바이스 시리얼 번호 설정 (실제로는 pet_id에 연결된 디바이스를 조회해야 함)
        device_serial = self._get_device_for_pet(db, pet_id)

        # 하이라이트 영상 URL 조회 (상위 5개)
        highlight_urls = self._get_highlight_videos_url(db, device_serial, date_str)

        # 정확히 5개의 URL을 반환하도록 보장
        while len(highlight_urls) < 5:
            # 부족한 경우 더미 URL 추가 (마지막 URL 재사용 또는 빈 문자열)
            if highlight_urls:
                highlight_urls.append(highlight_urls[-1])  # 마지막 URL 재사용
            else:
                highlight_urls.append("")  # 빈 문자열 추가

        # 히트맵 URL 조회 - 요청일자 기준으로 변경
        heatmap_url = self._get_heatmap_url(date_str, device_serial)

        # 시간별 활동량 데이터 조회
        time_activity = self._get_time_of_activity(db, device_serial, date_str)

        # 가장 활동적인 시간 계산
        most_active_hour = self._calculate_most_active_hour(time_activity)

        # 털 빠짐 점수 계산 및 abnormalBehavior 결정 - 요청일자 기준
        abnormal_behavior = self._calculate_shedding_score(db, device_serial, date_str)

        # 최근 7일 활동량 데이터 조회
        recent_activities = self._get_recent_activities(db, device_serial, query_date)

        # 결과 구성
        result = {
            "pet_id": pet_id,
            "abnormalBehavior": abnormal_behavior,  # 털 빠짐 점수 기반
            "highlightVideoUrl": highlight_urls[:5],  # 정확히 5개 URL 반환
            "mostActive": {  # 가장 활동적인 시간
                "start": most_active_hour,
                "end": most_active_hour + 1
            },
            "heatmapImageUrl": heatmap_url,  # null 반환 허용
            "timeOfActivity": time_activity,  # 하루 시간별 데이터
            "recentDatOfActivity": recent_activities  # 최근 7일 데이터
        }

        return result

    def _get_device_for_pet(self, db: Session, pet_id: str) -> str:
        """
        반려동물에 연결된 디바이스 시리얼 번호 조회

        Args:
            db: 데이터베이스 세션
            pet_id: 반려동물 ID

        Returns:
            str: 디바이스 시리얼 번호
        """
        # 실제로는 pet_id와 디바이스 간의 연결 정보를 조회해야 함
        # 여기서는 기본값 반환
        return "SFRXC12515GF00001"

    def _calculate_most_active_hour(self, time_activity: List[Dict[str, Any]]) -> int:
        """
        가장 활동적인 시간 계산

        Args:
            time_activity: 시간별 활동량 데이터

        Returns:
            int: 가장 활동적인 시간 (0-23)
        """
        if not time_activity:
            return 18  # 기본값: 저녁 6시

        # 활동량이 가장 높은 시간 찾기
        max_activity_hour = max(time_activity, key=lambda x: x["value"])
        return max_activity_hour["hour"]

    def _calculate_shedding_score(self, db: Session, device_serial: str, date_str: str) -> str:
        """
        털 빠짐 점수 계산 및 상태 결정 - yolo_results 테이블의 shedding_score 필드값만 사용

        Args:
            db: 데이터베이스 세션
            device_serial: 디바이스 시리얼 번호
            date_str: 날짜 문자열 (YYYYMMDD)

        Returns:
            str: 털 빠짐 상태 ('낮음', '중간', '높음')
        """
        try:
            logger.info(f"털 빠짐 점수 계산 시작: 디바이스={device_serial}, 날짜={date_str}")

            # shedding_score 필드값 직접 조회
            query = text("""
                         SELECT shedding_score
                         FROM capstone.yolo_results
                         WHERE device = :device_serial
                           AND date = :date_str
                           AND shedding_score IS NOT NULL
                         """)

            results = db.execute(query, {
                "device_serial": device_serial,
                "date_str": date_str
            }).fetchall()

            if not results:
                logger.warning(f"shedding_score 값이 없습니다: {device_serial}, {date_str}")
                return "없음"

            logger.info(f"shedding_score 결과 {len(results)}개 조회됨")

            # 결과에서 shedding_score 값 추출
            score_values = [float(row[0]) for row in results if row[0] is not None]

            if not score_values:
                logger.warning(f"유효한 shedding_score 값이 없습니다: {device_serial}, {date_str}")
                return "없음"

            # 가장 많이 등장한 값 찾기 (소수점 둘째 자리까지 반올림하여 빈도 계산)
            rounded_values = [round(val, 2) for val in score_values]
            value_counts = Counter(rounded_values)
            most_common_value = value_counts.most_common(1)[0][0]

            logger.info(f"가장 많이 나타난 shedding_score 값: {most_common_value} (빈도: {value_counts[most_common_value]})")

            # 구간별 상태 결정
            if most_common_value <= 0.33:
                return "낮음"
            elif most_common_value <= 0.67:
                return "중간"
            else:
                return "높음"

        except Exception as e:
            logger.error(f"털 빠짐 점수 계산 오류: {e}")
            return "없음"

    def _get_highlight_videos_url(self, db: Session, device_serial: str, date_str: str) -> List[str]:
        """
        active 값이 높은 상위 5개 시간대의 영상 URL 목록 반환

        Args:
            db: 데이터베이스 세션
            device_serial: 디바이스 시리얼 번호
            date_str: 날짜 문자열 (YYYYMMDD)

        Returns:
            List[str]: 하이라이트 영상 URL 목록
        """
        try:
            logger.info(f"하이라이트 영상 URL 조회 시작: 디바이스={device_serial}, 날짜={date_str}")

            # 해당 날짜의 상위 5개 active 값을 가진 레코드 조회
            query = text("""
                         SELECT "SN", "DATE", "TIME", active
                         FROM capstone.active_reports
                         WHERE "SN" = :sn
                           AND "DATE" = :date
                         ORDER BY active DESC LIMIT 10
                         """)

            results = db.execute(query, {"sn": device_serial, "date": date_str}).fetchall()

            if not results:
                # 해당 날짜에 데이터가 없으면 다른 날짜 데이터 조회 시도
                logger.info(f"지정 날짜 {date_str}에 데이터가 없어 다른 날짜 데이터 조회 시도")
                query = text("""
                             SELECT "SN", "DATE", "TIME", active
                             FROM capstone.active_reports
                             WHERE "SN" = :sn
                             ORDER BY active DESC LIMIT 10
                             """)

                results = db.execute(query, {"sn": device_serial}).fetchall()

                if not results:
                    logger.warning(f"활동량 데이터가 없습니다: {device_serial}")
                    return []

            logger.info(f"활동량 데이터 {len(results)}개 조회됨")

            # URL 목록
            urls = []

            # 각 레코드에 대해 URL 생성 시도 (최대 5개)
            for sn, record_date, time_str, active_val in results:
                if len(urls) >= 5:  # 이미 5개 URL이 생성되었으면 중단
                    break

                logger.info(f"레코드 처리: SN={sn}, DATE={record_date}, TIME={time_str}, active={active_val}")

                # S3 영상 파일 경로 구성
                video_key = f"stream/{sn}/{record_date}/{sn}_{record_date}_{time_str}.mp4"
                logger.info(f"하이라이트 영상 시도: {video_key}")

                # pre-signed URL 생성
                url = generate_presigned_url(video_key)

                if url:
                    logger.info(f"하이라이트 영상 URL 생성 성공: {video_key}")
                    urls.append(url)
                    continue  # 다음 레코드로 진행

                # 다른 형식의 경로도 시도
                alternate_paths = [
                    f"videos/{record_date}/{sn}_{time_str}.mp4",
                    f"videos/{sn}/{record_date}/{sn}_{record_date}_{time_str}.mp4",
                    f"videos/{record_date}/{sn}_{record_date}_{time_str}.mp4"
                ]

                for alt_path in alternate_paths:
                    logger.info(f"대체 경로 시도: {alt_path}")
                    url = generate_presigned_url(alt_path)
                    if url:
                        logger.info(f"대체 경로 URL 생성 성공: {alt_path}")
                        urls.append(url)
                        break  # 성공했으므로 다음 레코드로 진행

            logger.info(f"총 {len(urls)}개의 하이라이트 영상 URL 생성")
            return urls

        except Exception as e:
            logger.error(f"하이라이트 영상 URL 생성 오류: {e}")
            return []

    def _get_heatmap_url(self, date_str: str, device_serial: str) -> Optional[str]:
        """
        히트맵 이미지의 pre-signed URL 생성
        요청일자 기준으로 변경하고, 없으면 None 반환

        Args:
            date_str: 날짜 문자열 (YYYYMMDD)
            device_serial: 디바이스 시리얼 번호

        Returns:
            Optional[str]: 히트맵 이미지 URL 또는 None
        """
        try:
            logger.info(f"히트맵 URL 조회 시작: 디바이스={device_serial}, 날짜={date_str}")

            # S3 히트맵 파일 경로 시도 (요청일자 기준 경로만 시도)
            paths_to_try = [
                f"heatmap/{date_str}/{device_serial}_heatmap.png",
                f"heatmap/{date_str[:6]}/{device_serial}_heatmap.png",  # 월 단위 폴더
                f"heatmap/{device_serial}_{date_str}_heatmap.png",  # 루트 경로
            ]

            # 각 경로 시도
            for path in paths_to_try:
                logger.info(f"히트맵 경로 시도: {path}")
                url = generate_presigned_url(path)
                if url:
                    logger.info(f"히트맵 URL 생성 성공: {path}")
                    return url

            # 모든 시도가 실패하면 None 반환
            logger.warning(f"모든 히트맵 URL 생성 시도 실패: {device_serial}, {date_str}")
            return None

        except Exception as e:
            logger.error(f"히트맵 URL 생성 오류: {e}")
            return None

    def _get_time_of_activity(self, db: Session, device_serial: str, date_str: str) -> List[Dict[str, Any]]:
        """
        일일 시간별 활동량 데이터 조회

        Args:
            db: 데이터베이스 세션
            device_serial: 디바이스 시리얼 번호
            date_str: 날짜 문자열 (YYYYMMDD)

        Returns:
            List[Dict[str, Any]]: 시간별 활동량 데이터
        """
        try:
            # 해당 날짜의 활동량 데이터 조회
            query = text("""
                         SELECT "TIME", active
                         FROM capstone.active_reports
                         WHERE "SN" = :sn
                           AND "DATE" = :date
                         ORDER BY "TIME"
                         """)

            results = db.execute(query, {"sn": device_serial, "date": date_str}).fetchall()

            if not results:
                # 데이터가 없으면 빈 배열 반환
                logger.warning(f"활동량 데이터가 없습니다: {device_serial}, {date_str}")
                return []

            # 시간별 활동량 데이터 구성
            hourly_data = {}

            for time_str, active in results:
                # TIME 형식: HHMMSS에서 시간 추출
                hour = int(time_str[:2])

                if hour not in hourly_data:
                    hourly_data[hour] = {"total": 0, "count": 0}

                hourly_data[hour]["total"] += float(active)
                hourly_data[hour]["count"] += 1

            # 시간별 평균 활동량 계산
            result = []
            for hour in range(24):  # 0~23시
                if hour in hourly_data:
                    total = hourly_data[hour]["total"]
                    count = hourly_data[hour]["count"]
                    avg_value = round(total / count, 2) if count > 0 else 0

                    result.append({
                        "hour": hour,
                        "value": avg_value
                    })

            # 데이터가 없는 경우 빈 배열 반환
            if not result:
                return []

            return result

        except Exception as e:
            logger.error(f"활동량 데이터 조회 오류: {e}")
            # 오류 발생 시 빈 배열 반환
            return []

    def _get_recent_activities(self, db: Session, device_serial: str, query_date: date) -> List[Dict[str, Any]]:
        """
        최근 7일간의 일별 활동량 데이터 조회

        Args:
            db: 데이터베이스 세션
            device_serial: 디바이스 시리얼 번호
            query_date: 조회 날짜

        Returns:
            List[Dict[str, Any]]: 일별 활동량 데이터
        """
        try:
            # 최근 7일 날짜 계산 (당일 포함)
            dates = [(query_date - timedelta(days=i)) for i in range(7)]
            date_strs = [d.strftime("%Y%m%d") for d in dates]

            # 지정된 날짜들의 활동량 데이터 조회
            query = text("""
                         SELECT "DATE", active
                         FROM capstone.active_reports
                         WHERE "SN" = :sn
                           AND "DATE" IN :dates
                         ORDER BY "DATE", "TIME"
                         """)

            results = db.execute(query, {"sn": device_serial, "dates": tuple(date_strs)}).fetchall()

            # 일별 데이터 구성
            daily_data = {}

            for d in dates:
                date_str = d.strftime("%Y%m%d")
                day_str = f"{date_str[4:6]}.{date_str[6:8]}"  # "MM.DD" 형식
                daily_data[date_str] = {"day": day_str, "total": 0, "count": 0}

            # 데이터 처리
            for date_str, active in results:
                if date_str in daily_data:
                    daily_data[date_str]["total"] += float(active)
                    daily_data[date_str]["count"] += 1

            # 일별 평균 활동량 계산
            result = []
            for date_str, data in daily_data.items():
                avg_value = 0
                if data["count"] > 0:
                    avg_value = round(data["total"] / data["count"], 2)

                result.append({
                    "day": data["day"],
                    "value": avg_value
                })

            # 날짜 역순 정렬 (최신 날짜가 먼저)
            result.sort(key=lambda x: x["day"], reverse=True)

            # 데이터가 없는 경우 샘플 데이터 추가 (테스트용)
            if not any(item["value"] > 0 for item in result):
                # 모든 값이 0인 경우, 샘플 데이터로 대체 (테스트 환경용)
                sample_data = []
                for i in range(7):
                    day = (query_date - timedelta(days=i)).strftime("%m.%d")
                    sample_data.append({
                        "day": day,
                        "value": round(100 + i * 10 + (hash(day) % 30), 2)  # 약간의 랜덤성 추가
                    })
                return sample_data

            return result

        except Exception as e:
            logger.error(f"최근 활동량 데이터 조회 오류: {e}")
            # 오류 발생 시 빈 배열 반환
            return []