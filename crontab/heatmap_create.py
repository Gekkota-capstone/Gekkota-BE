"""
히트맵 생성 및 S3 업로드 스크립트
- RDS에서 capstone.yolo_results에서 YOLO 결과 데이터의 키포인트를 가져옴 (app.yolo_results가 아님)
- 히트맵 생성
- S3에 업로드 (/heatmap/date/sn_heatmap.png 형식)
- 매일 자정에 실행되어 전날 데이터로 히트맵 생성 (크론잡용, 한국시간 UTC+9 기준)
- 테스트 목적으로 현재 데이터(날짜 필터 없음)로 히트맵 생성 기능 분리 (S3 업로드 포함)
"""
import os
import sys
import argparse
import logging
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.ndimage import gaussian_filter
import cv2
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import boto3
import tempfile
import shutil

# crontab 1일 단위 실행

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
KST = pytz_timezone('Asia/Seoul')

def get_kst_now():
    return datetime.now(KST)

def connect_to_db():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL not set")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()

def connect_to_s3():
    load_dotenv()
    region = os.getenv("AWS_DEFAULT_REGION")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if not all([region, access_key, secret_key, bucket_name]):
        raise ValueError("AWS env variables not set")
    s3 = boto3.client("s3", region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    return s3, bucket_name

def fetch_yolo_data(db, device_serial, date_str=None):
    if date_str:
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        query = text(f"SELECT yolo_result FROM capstone.yolo_results WHERE device = '{device_serial}' AND date = '{formatted_date}'")
    else:
        query = text(f"SELECT yolo_result FROM capstone.yolo_results WHERE device = '{device_serial}'")
    result = db.execute(query)
    return [row[0] for row in result]

def generate_heatmap(yolo_results, output_path=None):
    """
    YOLO 결과에서 히트맵 생성

    Args:
        yolo_results: YOLO 결과 JSON 데이터 리스트
        output_path: 출력 파일 경로 (None이면 임시 파일 생성)

    Returns:
        생성된 히트맵 파일 경로
    """
    # 임시 파일 경로 생성
    if output_path is None:
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "heatmap.png")
        intermediate_path = os.path.join(temp_dir, "heatmap_intermediate.png")
    else:
        intermediate_path = f"{os.path.splitext(output_path)[0]}_intermediate.png"

    # 키포인트 좌표 추출
    keypoints_xy = []

    for yolo_result in yolo_results:
        try:
            # 이미 파싱된 딕셔너리 또는 JSON 문자열 처리
            data = yolo_result if isinstance(yolo_result, dict) else json.loads(yolo_result)

            if "keypoints" in data and len(data["keypoints"]) > 0:
                kps = data["keypoints"][0]  # 첫 번째 객체만 사용
                for kp in kps:
                    x, y = kp["xy"]
                    if x > 0 and y > 0:  # 유효한 키포인트만
                        keypoints_xy.append([x, y])
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.debug(f"Error processing keypoint: {str(e)}")
            continue

    # 충분한 키포인트가 있는지 확인
    keypoints_xy = np.array(keypoints_xy)
    if len(keypoints_xy) < 10:
        logger.warning(f"⚠️ Not enough valid keypoints: {len(keypoints_xy)}")
        return None

    logger.info(f"Processing {len(keypoints_xy)} keypoints")

    try:
        # 2D 히스토그램 생성
        num_bins_x, num_bins_y = 50, 50
        min_x, max_x = keypoints_xy[:, 0].min(), keypoints_xy[:, 0].max()
        min_y, max_y = keypoints_xy[:, 1].min(), keypoints_xy[:, 1].max()

        H, xedges, yedges = np.histogram2d(
            keypoints_xy[:, 1],
            keypoints_xy[:, 0],
            bins=[num_bins_y, num_bins_x],
            range=[[min_y, max_y], [min_x, max_x]]
        )

        # 가우시안 블러
        H_smooth = gaussian_filter(H, sigma=1.2)

        # 히트맵 중간 파일 생성
        plt.figure(figsize=(10, 6))
        plt.imshow(
            H_smooth,
            origin="lower",
            cmap="jet",
            norm=mcolors.LogNorm(vmin=1.0, vmax=H_smooth.max()),
            extent=[min_x, max_x, min_y, max_y],
            interpolation="bilinear"
        )
        plt.axis('off')
        plt.savefig(intermediate_path, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.close()

        # 후처리 (노이즈 제거)
        img = cv2.imread(intermediate_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)

        kernel = np.ones((5, 5), np.uint8)
        mask_dilated = cv2.dilate(mask, kernel, iterations=2)

        inpainted = cv2.inpaint(img, mask_dilated, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

        # 최종 히트맵 저장
        cv2.imwrite(output_path, inpainted)

        # 중간 파일 삭제
        if os.path.exists(intermediate_path):
            os.remove(intermediate_path)

        logger.info(f"✅ Heatmap generated successfully: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error generating heatmap: {str(e)}")
        return None


def upload_to_s3(s3_client, bucket_name, local_path, s3_key):
    try:
        s3_client.upload_file(local_path, bucket_name, s3_key)
        logger.info(f"Uploaded to S3: s3://{bucket_name}/{s3_key}")
        return True
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")
        return False

def process_device_heatmap(device_serial, date_str=None):
    db = None
    try:
        if date_str is None:
            date_str = get_kst_now().strftime("%Y%m%d")
        db = connect_to_db()
        yolo_results = fetch_yolo_data(db, device_serial, date_str)
        if not yolo_results:
            logger.warning("No YOLO data")
            return False
        heatmap_path = generate_heatmap(yolo_results)
        if not heatmap_path:
            return False
        s3_client, bucket = connect_to_s3()
        s3_key = f"heatmap/{date_str}/{device_serial}_heatmap.png"
        success = upload_to_s3(s3_client, bucket, heatmap_path, s3_key)
        os.remove(heatmap_path)
        os.rmdir(os.path.dirname(heatmap_path))
        return success
    finally:
        if db:
            db.close()

def process_previous_day_heatmap(device_serial):
    date_str = (get_kst_now() - timedelta(days=1)).strftime("%Y%m%d")
    return process_device_heatmap(device_serial, date_str)

def test_current_data_heatmap(device_serial):
    db = None
    try:
        logger.info("Generating test heatmap...")
        current_date = get_kst_now().strftime("%Y%m%d")
        db = connect_to_db()
        yolo_results = fetch_yolo_data(db, device_serial)
        if not yolo_results:
            return None, False
        heatmap_path = generate_heatmap(yolo_results)
        if not heatmap_path:
            return None, False
        s3_client, bucket = connect_to_s3()
        s3_key = f"heatmap/{current_date}/{device_serial}_heatmap_test.png"
        success = upload_to_s3(s3_client, bucket, heatmap_path, s3_key)
        os.remove(heatmap_path)
        os.rmdir(os.path.dirname(heatmap_path))
        return heatmap_path, success
    finally:
        if db:
            db.close()


# 고정 장치 시리얼 번호 설정
DEVICE_SN = "SFRXC12515GF00001"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="날짜 (YYYYMMDD)")
    parser.add_argument("--mode", choices=["cron", "test"], default="cron", help="모드: cron 또는 test")
    args = parser.parse_args()

    if args.mode == "cron":
        if args.date:
            success = process_device_heatmap(DEVICE_SN, args.date)
        else:
            success = process_previous_day_heatmap(DEVICE_SN)
    else:
        _, success = test_current_data_heatmap(DEVICE_SN)

    if success:
        logger.info("✅ Heatmap process complete")
        return 0
    else:
        logger.error("❌ Heatmap process failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
