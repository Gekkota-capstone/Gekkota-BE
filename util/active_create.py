# /util/active_create.py

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
from service.active_report_service import ActiveReportService

# 로깅 설정
logger = logging.getLogger(__name__)

# 고정 장치 시리얼 번호 설정
DEVICE_SN = "SFRXC12515GF00001"


def fetch_yolo_data_by_time_range(session, device_serial, start_time, end_time):
    """
    RDS에서 특정 시간 범위의 YOLO 감지 결과 가져오기
    타임스탬프 기준으로 조회
    """
    try:
        # 시간 형식 변환 (YYYYMMDD_HHMMSS)
        start_str = start_time.strftime("%Y%m%d_%H%M%S")
        end_str = end_time.strftime("%Y%m%d_%H%M%S")

        # SQL 쿼리 구성
        query = text(f"""
            SELECT image, device, date, yolo_result 
            FROM capstone.yolo_results 
            WHERE device = '{device_serial}' 
            AND yolo_result->>'timestamp' >= '{start_str}' 
            AND yolo_result->>'timestamp' < '{end_str}'
            ORDER BY yolo_result->>'timestamp'
        """)

        result = session.execute(query)

        # 결과를 DataFrame으로 변환
        rows = []
        for row in result:
            rows.append({
                "image": row[0],
                "device": row[1],
                "date": row[2],
                "yolo_result": row[3]  # JSONB 타입은 자동으로 Python 딕셔너리로 변환됨
            })

        df = pd.DataFrame(rows)
        logger.info(f"Retrieved {len(df)} YOLO records for device {device_serial} in time range")
        return df

    except Exception as e:
        logger.error(f"Error fetching YOLO data: {str(e)}")
        raise


def extract_center_from_yolo(yolo_data):
    """YOLO 결과에서 중심 좌표와 타임스탬프 추출"""
    try:
        boxes = yolo_data.get("boxes", [])
        if boxes:
            x1, y1, x2, y2 = boxes[0]["xyxy"]
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            timestamp_str = yolo_data.get("timestamp")
            if timestamp_str:
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                return timestamp, (center_x, center_y)
    except Exception as e:
        logger.error(f"Error extracting center: {str(e)}")

    return None, None


def calculate_activity(df, interval_minutes=1, start_time=None, end_time=None):
    """
    활동량 계산
    데이터가 부족해도 0으로 기록

    Args:
        df: YOLO 데이터 DataFrame
        interval_minutes: 계산 간격(분) - 1분으로 변경
        start_time: 시작 시간 (None이면 데이터에서 추출)
        end_time: 종료 시간 (None이면 데이터에서 추출)

    Returns:
        DataFrame: 활동량 데이터
    """
    # 중심 좌표 추출
    center_data = []
    for yolo_data in df['yolo_result']:
        ts, center = extract_center_from_yolo(yolo_data)
        if ts and center:
            center_data.append((ts, center))

    # 시간 순 정렬
    center_data.sort(key=lambda x: x[0])

    # 결과를 저장할 DataFrame 준비
    rows = []
    device_sn = df['device'].iloc[0] if not df.empty else DEVICE_SN

    # 시간 범위 설정
    if start_time and end_time:
        # 시간 범위가 제공된 경우
        time_range_start = start_time.replace(tzinfo=None)
        time_range_end = end_time.replace(tzinfo=None)
    elif len(center_data) >= 2:
        # 데이터에서 시간 범위 추출
        time_range_start = center_data[0][0]
        time_range_end = center_data[-1][0]
    elif not df.empty and 'yolo_result' in df.columns and len(df) > 0:
        # 중심 좌표는 추출되지 않았지만 YOLO 데이터가 있는 경우
        try:
            timestamps = []
            for yolo_data in df['yolo_result']:
                ts_str = yolo_data.get('timestamp')
                if ts_str:
                    ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
                    timestamps.append(ts)

            if timestamps:
                timestamps.sort()
                time_range_start = timestamps[0]
                time_range_end = timestamps[-1]
            else:
                # 타임스탬프를 추출할 수 없는 경우 현재 시간 사용
                current_time = datetime.now()
                time_range_start = current_time - timedelta(minutes=interval_minutes)
                time_range_end = current_time
        except Exception as e:
            logger.error(f"Error extracting timestamps: {e}")
            # 오류 발생 시 현재 시간 사용
            current_time = datetime.now()
            time_range_start = current_time - timedelta(minutes=interval_minutes)
            time_range_end = current_time
    else:
        # 데이터가 없는 경우 현재 시간 사용
        current_time = datetime.now()
        time_range_start = current_time - timedelta(minutes=interval_minutes)
        time_range_end = current_time

    # 1분 간격 계산
    interval_start = time_range_start.replace(
        minute=time_range_start.minute,
        second=0,
        microsecond=0
    )

    # 필요한 경우 interval_start를 조정하여 time_range_start 이전으로 설정
    while interval_start > time_range_start:
        interval_start -= timedelta(minutes=interval_minutes)

    # 다음 간격이 time_range_end를 넘을 때까지 반복
    current_interval = interval_start
    while current_interval < time_range_end:
        next_interval = current_interval + timedelta(minutes=interval_minutes)

        # 현재 간격의 활동량 계산
        interval_activity = 0.0

        # 중심 좌표가 충분히 있는 경우
        if len(center_data) >= 2:
            for i in range(1, len(center_data)):
                prev_ts, prev_center = center_data[i - 1]
                curr_ts, curr_center = center_data[i]

                # 현재 간격에 포함되는 경우만 계산
                if (current_interval <= prev_ts < next_interval or
                        current_interval <= curr_ts < next_interval):
                    dist = np.linalg.norm(np.array(curr_center) - np.array(prev_center))
                    interval_activity += dist

        # 결과 추가
        date_str = current_interval.strftime('%Y%m%d')
        time_str = f"{current_interval.strftime('%H%M')}00"

        rows.append({
            "SN": device_sn,
            "DATE": date_str,
            "TIME": time_str,
            "active": round(interval_activity, 2)
        })

        # 다음 간격으로 이동
        current_interval = next_interval

    return pd.DataFrame(rows)


def process_current_interval(session: Session, start_time: datetime, end_time: datetime):
    """현재 1분 시간 간격에 대한 활동량 처리"""
    try:
        # ActiveReportService 인스턴스 생성
        active_report_service = ActiveReportService()

        # YOLO 데이터 가져오기
        df = fetch_yolo_data_by_time_range(session, DEVICE_SN, start_time, end_time)

        # 데이터가 없어도 빈 DataFrame을 생성하여 0으로 기록
        if df.empty:
            logger.warning(f"No YOLO data found for device {DEVICE_SN}")
            # 빈 DataFrame을 생성하여 0으로 기록
            empty_df = pd.DataFrame([{
                "image": None,
                "device": DEVICE_SN,
                "date": start_time.strftime("%Y%m%d"),
                "yolo_result": {"timestamp": start_time.strftime("%Y%m%d_%H%M%S")}
            }])
            activity_df = calculate_activity(empty_df, start_time=start_time, end_time=end_time)
        else:
            # 활동량 계산 (시작/종료 시간 명시적 전달)
            activity_df = calculate_activity(df, start_time=start_time, end_time=end_time)

        if activity_df.empty:
            logger.warning(f"Failed to create activity dataframe for device {DEVICE_SN}")
            return False

        # DB에 저장
        saved_count = active_report_service.save_activity_data(session, activity_df)
        logger.info(f"Saved {saved_count} records to database for device {DEVICE_SN}")

        return True

    except Exception as e:
        logger.error(f"Error processing device {DEVICE_SN}: {str(e)}")
        return False