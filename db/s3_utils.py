# /db/s3_utils.py

import boto3
import os
from dotenv import load_dotenv
import logging
from typing import Optional

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# S3 클라이언트 초기화
s3_client = boto3.client(
    "s3",
    region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)


def get_s3_client():
    """
    S3 클라이언트 반환

    Returns:
        boto3.client: S3 클라이언트
    """
    return s3_client


def get_bucket_name():
    """
    S3 버킷 이름 반환

    Returns:
        str: S3 버킷 이름
    """
    return S3_BUCKET


def check_object_exists(key: str) -> bool:
    """
    S3 객체 존재 여부 확인

    Args:
        key: S3 객체 키

    Returns:
        bool: 객체 존재 여부
    """
    try:
        s3_client.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except Exception:
        return False


def generate_presigned_url(key: str, expiration: int = 3600) -> Optional[str]:
    """
    S3 객체에 대한 pre-signed URL 생성

    Args:
        key: S3 객체 키
        expiration: URL 만료 시간 (초)

    Returns:
        str: pre-signed URL 또는 None
    """
    try:
        # 객체 존재 여부 확인
        if not check_object_exists(key):
            logger.warning(f"S3 객체가 존재하지 않습니다: {key}")
            return None

        # pre-signed URL 생성
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': key},
            ExpiresIn=expiration
        )

        return url

    except Exception as e:
        logger.error(f"pre-signed URL 생성 오류: {e}")
        return None