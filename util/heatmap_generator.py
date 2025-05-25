# /util/heatmap_generator.py

import os
import logging
import pandas as pd
import numpy as np
import json
# matplotlib 백엔드를 GUI가 필요없는 'Agg'로 설정 (중요!)
import matplotlib

matplotlib.use('Agg')  # 반드시 pyplot 임포트 전에 설정해야 함
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.ndimage import gaussian_filter
import cv2
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
import boto3
import tempfile
import uuid

# 로깅 설정
logger = logging.getLogger(__name__)

# 한국 시간대 설정
KST = pytz_timezone('Asia/Seoul')

# 고정 장치 시리얼 번호 설정
DEVICE_SN = "SFRXC12515GF00001"


def get_kst_now():
    """현재 한국 시간 반환"""
    return datetime.now(KST)


def connect_to_s3():
    """S3 클라이언트 연결"""
    try:
        # 환경 변수에서 AWS 설정 가져오기
        region = os.getenv("AWS_DEFAULT_REGION")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        bucket_name = os.getenv("S3_BUCKET_NAME")

        if not all([region, access_key, secret_key, bucket_name]):
            logger.error("AWS 환경 변수가 설정되지 않았습니다.")
            return None, None

        s3 = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

        return s3, bucket_name
    except Exception as e:
        logger.error(f"S3 연결 실패: {e}")
        return None, None


def upload_to_s3(s3_client, bucket_name, local_path, s3_key):
    """
    S3에 파일 업로드

    Args:
        s3_client: S3 클라이언트
        bucket_name: 버킷 이름
        local_path: 로컬 파일 경로
        s3_key: S3 키

    Returns:
        bool: 업로드 성공 여부
        str: S3 URL 또는 None
    """
    try:
        if not os.path.exists(local_path):
            logger.error(f"업로드할 파일이 존재하지 않습니다: {local_path}")
            return False, None

        s3_client.upload_file(local_path, bucket_name, s3_key)
        logger.info(f"S3 업로드 완료: s3://{bucket_name}/{s3_key}")
        # S3 URL 반환
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        return True, s3_url
    except Exception as e:
        logger.error(f"S3 업로드 실패: {e}")
        return False, None


def cleanup_temp_files(file_path):
    """임시 파일 및 디렉토리 정리"""
    try:
        if file_path and os.path.exists(file_path):
            # 파일 삭제
            os.unlink(file_path)

            # 부모 디렉토리가 비어있으면 삭제
            parent_dir = os.path.dirname(file_path)
            if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                os.rmdir(parent_dir)

            logger.info(f"임시 파일 정리 완료: {file_path}")
    except Exception as e:
        logger.error(f"임시 파일 정리 오류: {e}")


# /util/heatmap_generator.py (주요 부분만 수정)

# ... 기존 코드 ...

def fetch_yolo_data(session: Session, device_serial: str, date_str=None):
    """
    RDS에서 YOLO 결과 데이터 가져오기

    Args:
        session: 데이터베이스 세션
        device_serial: 장치 시리얼 번호
        date_str: 날짜 문자열 (YYYYMMDD 형식)

    Returns:
        YOLO 결과 데이터 리스트
    """
    try:
        if date_str:
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            query = text(f"""
                SELECT yolo_result 
                FROM capstone.yolo_results 
                WHERE device = '{device_serial}' 
                AND date = '{formatted_date}'
            """)
            logger.info(f"날짜 {formatted_date}의 YOLO 데이터 조회 중...")
        else:
            query = text(f"""
                SELECT yolo_result 
                FROM capstone.yolo_results 
                WHERE device = '{device_serial}'
                ORDER BY yolo_result->>'timestamp' DESC
                LIMIT 1000  -- 데이터 제한 추가
            """)
            logger.info(f"전체 기간(최근 1000건)의 YOLO 데이터 조회 중...")

        result = session.execute(query)
        yolo_results = [row[0] for row in result]

        logger.info(f"디바이스 {device_serial}에서 {len(yolo_results)}개의 YOLO 데이터를 가져왔습니다.")

        # 첫 번째와 마지막 데이터의 타임스탬프 확인 (로그 용)
        if yolo_results:
            try:
                first_timestamp = None
                last_timestamp = None

                for data in yolo_results:
                    if isinstance(data, dict) and "timestamp" in data:
                        ts = data["timestamp"]
                        if first_timestamp is None:
                            first_timestamp = ts
                        last_timestamp = ts
                    elif isinstance(data, str):
                        data_dict = json.loads(data)
                        if "timestamp" in data_dict:
                            ts = data_dict["timestamp"]
                            if first_timestamp is None:
                                first_timestamp = ts
                            last_timestamp = ts

                if first_timestamp and last_timestamp:
                    logger.info(f"데이터 시간 범위: {first_timestamp} ~ {last_timestamp}")
            except Exception as e:
                logger.debug(f"타임스탬프 추출 중 오류: {e}")

        return yolo_results
    except Exception as e:
        logger.error(f"YOLO 데이터 조회 실패: {e}")
        return []


def generate_heatmap(yolo_results, output_path=None):
    """
    YOLO 결과에서 히트맵 생성 (비GUI 모드로 수정)

    Args:
        yolo_results: YOLO 결과 JSON 데이터 리스트
        output_path: 출력 파일 경로 (None이면 임시 파일 생성)

    Returns:
        생성된 히트맵 파일 경로
    """
    # 임시 디렉토리 생성 (고유 ID 사용)
    temp_dir = tempfile.mkdtemp(prefix=f"heatmap_{uuid.uuid4().hex}_")

    if output_path is None:
        output_path = os.path.join(temp_dir, "heatmap.png")

    intermediate_path = os.path.join(temp_dir, "heatmap_intermediate.png")

    # 키포인트 좌표 추출
    keypoints_xy = []
    processed_count = 0
    error_count = 0

    for yolo_result in yolo_results:
        processed_count += 1
        try:
            # 이미 파싱된 딕셔너리 또는 JSON 문자열 처리
            data = yolo_result if isinstance(yolo_result, dict) else json.loads(yolo_result)

            if "keypoints" in data and len(data["keypoints"]) > 0:
                kps = data["keypoints"][0]  # 첫 번째 객체만 사용
                for kp in kps:
                    if "xy" in kp and len(kp["xy"]) == 2:
                        x, y = kp["xy"]
                        if x > 0 and y > 0:  # 유효한 키포인트만
                            keypoints_xy.append([x, y])
        except (json.JSONDecodeError, KeyError, TypeError, IndexError) as e:
            error_count += 1
            if error_count <= 5:  # 처음 몇 개의 오류만 자세히 기록
                logger.debug(f"키포인트 처리 오류 ({processed_count}번째 데이터): {str(e)}")
            continue

    # 처리 통계 기록
    logger.info(f"총 {processed_count}개의 YOLO 데이터 중 {error_count}개 처리 오류, {len(keypoints_xy)}개의 유효 키포인트 추출")

    # 충분한 키포인트가 있는지 확인
    if not keypoints_xy or len(keypoints_xy) < 10:
        logger.warning(f"⚠️ 유효한 키포인트가 부족합니다: {len(keypoints_xy)}")
        # 임시 디렉토리 정리
        try:
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                os.rmdir(temp_dir)
        except Exception as e:
            logger.error(f"임시 디렉토리 정리 오류: {e}")
        return None

    keypoints_xy = np.array(keypoints_xy)
    logger.info(f"{len(keypoints_xy)}개의 키포인트 처리 중")

    try:
        # 2D 히스토그램 생성
        num_bins_x, num_bins_y = 50, 50

        # 데이터 범위 설정 (이상치 제거)
        x_data = keypoints_xy[:, 0]
        y_data = keypoints_xy[:, 1]

        # 양쪽 끝 1% 제거 (이상치 제거)
        x_min, x_max = np.percentile(x_data, 1), np.percentile(x_data, 99)
        y_min, y_max = np.percentile(y_data, 1), np.percentile(y_data, 99)

        logger.info(f"데이터 범위: X({x_min:.1f}~{x_max:.1f}), Y({y_min:.1f}~{y_max:.1f})")

        # 히스토그램 계산
        H, xedges, yedges = np.histogram2d(
            y_data,
            x_data,
            bins=[num_bins_y, num_bins_x],
            range=[[y_min, y_max], [x_min, x_max]],
            density=False
        )

        # 가우시안 블러 적용
        H_smooth = gaussian_filter(H, sigma=1.2)

        # 히트맵 중간 파일 생성 (Agg 백엔드 사용)
        # 고정된 비율의 이미지 생성 (16:9)
        width, height = 16, 9
        dpi = 100  # 해상도 (높일수록 고해상도)

        # 비율 계산
        data_aspect_ratio = (x_max - x_min) / (y_max - y_min)

        # 고정 비율로 설정 (16:9 또는 4:3 등)
        target_aspect_ratio = width / height

        # 실제 출력 크기 계산 (인치 단위)
        if data_aspect_ratio > target_aspect_ratio:
            # 너비에 맞추기
            figwidth = width
            figheight = width / data_aspect_ratio
        else:
            # 높이에 맞추기
            figheight = height
            figwidth = height * data_aspect_ratio

        # 그림 생성
        plt.figure(figsize=(figwidth, figheight), dpi=dpi)
        plt.imshow(
            H_smooth,
            origin="lower",
            cmap="jet",
            norm=mcolors.LogNorm(vmin=max(1.0, H_smooth.max() * 0.01), vmax=H_smooth.max()),
            extent=[x_min, x_max, y_min, y_max],
            interpolation="bilinear"
        )
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(intermediate_path, bbox_inches='tight', pad_inches=0, dpi=dpi)
        plt.close()  # 명시적으로 닫기

        # 후처리 정보
        if os.path.exists(intermediate_path):
            filesize = os.path.getsize(intermediate_path) / 1024  # KB
            logger.info(f"중간 파일 생성 완료: {intermediate_path} ({filesize:.1f}KB)")

        # 후처리 (노이즈 제거)
        img = cv2.imread(intermediate_path)
        if img is None:
            logger.error(f"중간 파일을 읽을 수 없습니다: {intermediate_path}")
            raise ValueError("이미지 로드 실패")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)

        kernel = np.ones((5, 5), np.uint8)
        mask_dilated = cv2.dilate(mask, kernel, iterations=2)

        inpainted = cv2.inpaint(img, mask_dilated, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

        # 최종 히트맵 저장
        cv2.imwrite(output_path, inpainted)

        # 최종 파일 정보
        if os.path.exists(output_path):
            filesize = os.path.getsize(output_path) / 1024  # KB
            logger.info(f"최종 히트맵 파일 생성 완료: {output_path} ({filesize:.1f}KB)")

        # 중간 파일 삭제
        if os.path.exists(intermediate_path):
            os.unlink(intermediate_path)

        logger.info(f"✅ 히트맵 생성 완료: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"히트맵 생성 오류: {str(e)}")
        # 임시 디렉토리 정리
        try:
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                os.rmdir(temp_dir)
        except Exception as cleanup_error:
            logger.error(f"임시 디렉토리 정리 오류: {cleanup_error}")
        return None