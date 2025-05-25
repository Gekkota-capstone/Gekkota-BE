"""
활동량 데이터 생성 및 저장 스크립트
- RDS에서 capstone.yolo_results에서 YOLO 결과 데이터를 불러옴 (app.yolo_results가 아님)
- 최근 15분 단위 활동량 데이터 계산
- 계산된 데이터를 capstone.active_reports 테이블에 저장
- 테이블이 없는 경우 자동 생성
- 크론잡으로 매 시간 15분마다 실행 (00:15, 00:30, 00:45, 01:00, ...)
- 한국시간(UTC+9) 기준
"""
#active_create.py
import os
import sys
import argparse
import logging
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta, date
from pytz import timezone as pytz_timezone
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Float, insert, inspect
from sqlalchemy.orm import sessionmaker

# 5분 단위 실행 crontab

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 한국 시간대 설정
KST = pytz_timezone('Asia/Seoul')


def get_kst_now():
    """현재 한국 시간 반환"""
    return datetime.now(KST)


def connect_to_db():
    """데이터베이스 연결"""
    # .env 파일 로드
    load_dotenv()

    # 데이터베이스 URL 가져오기
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    # SQLAlchemy 엔진 및 세션 생성
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return engine, Session()


def ensure_active_reports_table_exists(engine):
    """
    capstone.active_reports 테이블이 존재하는지 확인하고 없으면 생성
    """
    inspector = inspect(engine)
    table_exists = 'active_reports' in inspector.get_table_names(schema='capstone')
    
    if not table_exists:
        logger.info("Creating table capstone.active_reports...")
        metadata = MetaData()
        
        # active_reports 테이블 정의
        active_reports = Table(
            'active_reports', 
            metadata,
            Column('SN', String(255), primary_key=True, nullable=False),
            Column('DATE', String(8), primary_key=True, nullable=False),
            Column('TIME', String(9), primary_key=True, nullable=False),
            Column('active', Float, nullable=False),
            schema='capstone'
        )
        
        # 스키마 존재 여부 확인
        schema_exists = 'capstone' in inspector.get_schema_names()
        
        # 스키마가 없으면 생성
        if not schema_exists:
            engine.execute(text("CREATE SCHEMA IF NOT EXISTS capstone"))
            logger.info("Created schema 'capstone'")
        
        # 테이블 생성
        metadata.create_all(engine)
        logger.info("Table capstone.active_reports created successfully")
    else:
        logger.info("Table capstone.active_reports already exists")


def get_time_range():
    """
    현재 시간 기준으로 처리할 시간 범위 반환
    현재 시간이 15:23이면 -> 15:15~15:20 처리
    현재 시간이 15:37이면 -> 15:30~15:35 처리
    매 5분마다 실행되는 것을 가정
    """
    now = get_kst_now()

    current_minute = now.minute
    base_minute = (current_minute // 5) * 5

    end_time = now.replace(minute=base_minute, second=0, microsecond=0)
    start_time = end_time - timedelta(minutes=5)

    logger.info(f"Processing data for time range: {start_time} to {end_time}")
    
    return start_time, end_time



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


def fetch_all_yolo_data(session, device_serial):
    """
    RDS에서 해당 기기의 모든 YOLO 감지 결과 가져오기
    테스트 모드용
    """
    try:
        # SQL 쿼리 구성
        query = text(f"""
            SELECT image, device, date, yolo_result 
            FROM capstone.yolo_results 
            WHERE device = '{device_serial}'
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
        logger.info(f"Retrieved {len(df)} YOLO records for device {device_serial} (ALL DATA)")
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


def calculate_activity(df, interval_minutes=5):
    """
    활동량 계산
    15분 데이터를 5분 단위로 나누어 계산
    """
    # 중심 좌표 추출
    center_data = []
    for yolo_data in df['yolo_result']:
        ts, center = extract_center_from_yolo(yolo_data)
        if ts and center:
            center_data.append((ts, center))

    # 시간 순 정렬
    center_data.sort(key=lambda x: x[0])

    if len(center_data) < 2:
        logger.warning("Not enough data points to calculate activity")
        return pd.DataFrame()

    # 연속 프레임 간 거리 계산
    distances = []
    for i in range(1, len(center_data)):
        prev_ts, prev_center = center_data[i - 1]
        curr_ts, curr_center = center_data[i]
        dist = np.linalg.norm(np.array(curr_center) - np.array(prev_center))
        distances.append((curr_ts, dist))

    # 5분 단위 활동량 누적
    activity_log = {}
    for ts, dist in distances:
        base_min = (ts.minute // interval_minutes) * interval_minutes
        interval_start = ts.replace(minute=base_min, second=0, microsecond=0)
        interval_end = interval_start + timedelta(minutes=interval_minutes)
        key = (ts.date(), interval_start.strftime('%H%M'), interval_end.strftime('%H%M'))
        activity_log[key] = activity_log.get(key, 0) + dist

    # 결과 포맷 구성 (SN, DATE, TIME, active)
    device_sn = df['device'].iloc[0] if not df.empty else None
    rows = []

    if device_sn:
        for (date_obj, start_str, end_str), movement in sorted(activity_log.items()):
            date_str = date_obj.strftime('%Y%m%d')
            time_range = f"{start_str}00"
            rows.append({
                "SN": device_sn,                # SN 컬럼 (character varying 255)
                "DATE": date_str,               # DATE 컬럼 (character varying 8)
                "TIME": time_range,             # TIME 컬럼 (character varying 9)
                "active": round(movement, 2)    # active 컬럼 (double precision)
            })

    return pd.DataFrame(rows)


def save_activity_data(engine, session, activity_df):
    """활동량 데이터를 capstone.active_reports 테이블에 저장"""
    if activity_df.empty:
        logger.warning("No activity data to save")
        return 0

    try:
        count = 0
        for _, row in activity_df.iterrows():
            # 이미 존재하는 데이터 확인 쿼리
            check_query = text(f"""
                SELECT COUNT(*) FROM capstone.active_reports 
                WHERE "SN" = '{row["SN"]}' AND "DATE" = '{row["DATE"]}' AND "TIME" = '{row["TIME"]}'
            """)
            result = session.execute(check_query).scalar()

            if result > 0:
                # 기존 데이터 업데이트
                update_query = text(f"""
                    UPDATE capstone.active_reports 
                    SET active = {row["active"]} 
                    WHERE "SN" = '{row["SN"]}' AND "DATE" = '{row["DATE"]}' AND "TIME" = '{row["TIME"]}'
                """)
                session.execute(update_query)
                logger.debug(f"Updated activity for {row['SN']} on {row['DATE']} at {row['TIME']}")
            else:
                # 새 데이터 삽입
                insert_query = text(f"""
                    INSERT INTO capstone.active_reports ("SN", "DATE", "TIME", active)
                    VALUES ('{row["SN"]}', '{row["DATE"]}', '{row["TIME"]}', {row["active"]})
                """)
                session.execute(insert_query)
                logger.debug(f"Inserted activity for {row['SN']} on {row['DATE']} at {row['TIME']}")

            count += 1

        session.commit()
        logger.info(f"Saved {count} activity records to database")
        return count

    except Exception as e:
        session.rollback()
        logger.error(f"Error saving activity data: {str(e)}")
        raise


def process_current_interval(device_serial, test_mode=False):
    """
    현재 15분 시간 간격에 대한 활동량 처리
    (또는 테스트 모드인 경우 모든 데이터)
    """
    engine = None
    session = None
    try:
        # DB 연결
        engine, session = connect_to_db()
        
        # capstone.active_reports 테이블 확인/생성
        ensure_active_reports_table_exists(engine)

        if test_mode:
            # 테스트 모드: 모든 데이터 사용
            logger.info(f"Test mode: Using ALL data for device {device_serial}")
            df = fetch_all_yolo_data(session, device_serial)
        else:
            # 일반 모드: 최근 15분 간격 사용
            start_time, end_time = get_time_range()
            df = fetch_yolo_data_by_time_range(session, device_serial, start_time, end_time)

        if df.empty:
            logger.warning(f"No YOLO data found for device {device_serial}")
            return False

        # 활동량 계산
        activity_df = calculate_activity(df)

        if activity_df.empty:
            logger.warning(f"Could not calculate activity for device {device_serial}")
            return False

        # DB에 저장
        saved_count = save_activity_data(engine, session, activity_df)
        logger.info(f"Saved {saved_count} records to database for device {device_serial}")

        return True

    except Exception as e:
        logger.error(f"Error processing device {device_serial}: {str(e)}")
        return False
    finally:
        if session:
            session.close()

# 고정 장치 시리얼 번호 설정
DEVICE_SN = "SFRXC12515GF00001"

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="Generate and save activity data")
    parser.add_argument("--test", action="store_true", help="Test mode: process ALL data for this device")
    args = parser.parse_args()

    # 모드에 따라 처리
    success = process_current_interval(
        device_serial=DEVICE_SN,
        test_mode=args.test
    )

    if success:
        logger.info(f"Successfully processed activity for device {DEVICE_SN}")
        return 0
    else:
        logger.error(f"Failed to process activity for device {DEVICE_SN}")
        return 1


if __name__ == "__main__":
    sys.exit(main())