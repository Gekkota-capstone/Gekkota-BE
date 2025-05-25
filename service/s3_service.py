# /service/s3_service.py

from db.s3_utils import s3_client, S3_BUCKET, REGION
from datetime import datetime
from sqlalchemy.orm import Session
import re
from typing import List, Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

from repository.device_repository import DeviceRepository

# Initialize repository
device_repository = DeviceRepository()


def extract_date_from_filename(filename: str) -> str:
    match = re.search(r"_(\d{8})_", filename)
    if match:
        return match.group(1)
    else:
        return datetime.utcnow().strftime("%Y%m%d")


def get_content_type_by_extension(filename: str) -> str:
    if filename.endswith(".mp4"):
        return "video/mp4"
    elif filename.endswith(".jpg"):
        return "image/jpeg"
    elif filename.endswith(".zip"):
        return "application/zip"
    else:
        return "application/octet-stream"


def generate_presigned_upload_url(
        db: Session,
        sn: str,
        filename: str,
        folder: str,
        expires_in: int = 300
) -> dict:
    device = device_repository.get_device_by_sn(db, sn)
    if not device:
        raise FileNotFoundError("Serial Number not found")

    if not filename.startswith(sn):
        raise ValueError("Filename does not match SN")

    date = extract_date_from_filename(filename)
    object_key = f"{folder}/{sn}/{date}/{filename}"
    content_type = get_content_type_by_extension(filename)

    try:
        url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": object_key,
                "ContentType": content_type
            },
            ExpiresIn=expires_in
        )
        return {
            "upload_url": url,
            "s3_key": object_key,
            "expires_in": expires_in
        }
    except Exception as e:
        raise RuntimeError(f"Failed to generate presigned URL: {e}")


def generate_video_presigned_url(
        db: Session,
        sn: str,
        firebase_uid: str,
        date: str,
        time: str,
        expires_in: int = 3600
) -> Dict[str, Any]:
    """
    Generate a pre-signed URL for a specific video file based on SN, date, and time.

    Args:
        db: Database session
        sn: Device serial number
        firebase_uid: User firebase UID
        date: Date in YYYYMMDD format
        time: Time in HHMMSS format
        expires_in: URL expiration time in seconds

    Returns:
        Dictionary containing video metadata and pre-signed URL
    """
    # Verify device exists and belongs to the specified user
    device = device_repository.get_device_by_sn(db, sn)
    if not device:
        raise FileNotFoundError("Serial Number not found")

    if device.UID != firebase_uid:
        raise ValueError("Device does not belong to this user")

    # Format date if necessary
    if re.match(r"\d{4}-\d{2}-\d{2}", date):
        # Convert from YYYY-MM-DD to YYYYMMDD
        date = date.replace("-", "")
    elif not re.match(r"\d{8}", date):
        raise ValueError("Invalid date format. Use YYYYMMDD or YYYY-MM-DD")

    # Format time if necessary
    if re.match(r"\d{2}:\d{2}:\d{2}", time):
        # Convert from HH:MM:SS to HHMMSS
        time = time.replace(":", "")
    elif not re.match(r"\d{6}", time):
        raise ValueError("Invalid time format. Use HHMMSS or HH:MM:SS")

    # Construct filename and object key
    filename = f"{sn}_{date}_{time}.mp4"
    object_key = f"stream/{sn}/{date}/{filename}"

    # Check if the object exists
    try:
        s3_client.head_object(Bucket=S3_BUCKET, Key=object_key)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            raise FileNotFoundError(f"Video file not found: {filename}")
        else:
            raise RuntimeError(f"Error checking for video file: {str(e)}")

    # Generate presigned URL
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': object_key
            },
            ExpiresIn=expires_in
        )

        # Get object metadata
        response = s3_client.head_object(Bucket=S3_BUCKET, Key=object_key)

        return {
            "filename": filename,
            "download_url": url,
            "s3_key": object_key,
            "size": response.get('ContentLength', 0),
            "last_modified": response.get('LastModified').isoformat() if 'LastModified' in response else None,
            "content_type": response.get('ContentType', 'video/mp4'),
            "expires_in": expires_in
        }

    except ClientError as e:
        raise RuntimeError(f"Failed to generate presigned URL: {str(e)}")


def list_videos_by_date(
        db: Session,
        sn: str,
        firebase_uid: str,
        date: str,
        expires_in: int = 3600
) -> List[Dict[str, Any]]:
    """
    List all videos for a specific date and generate pre-signed URLs for each.

    Args:
        db: Database session
        sn: Device serial number
        firebase_uid: User firebase UID
        date: Date in YYYYMMDD format
        expires_in: URL expiration time in seconds

    Returns:
        List of dictionaries containing video metadata and pre-signed URLs
    """
    # Verify device exists and belongs to the specified user
    device = device_repository.get_device_by_sn(db, sn)
    if not device:
        raise FileNotFoundError("Serial Number not found")

    if device.UID != firebase_uid:
        raise ValueError("Device does not belong to this user")

    # Format date if necessary
    if re.match(r"\d{4}-\d{2}-\d{2}", date):
        # Convert from YYYY-MM-DD to YYYYMMDD
        date = date.replace("-", "")
    elif not re.match(r"\d{8}", date):
        raise ValueError("Invalid date format. Use YYYYMMDD or YYYY-MM-DD")

    # List all objects in the specific date folder
    prefix = f"stream/{sn}/{date}/"

    try:
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=prefix
        )

        # If no objects found
        if 'Contents' not in response:
            return []

        # Generate presigned URLs for each video
        result = []
        for obj in response['Contents']:
            key = obj['Key']
            filename = key.split('/')[-1]

            # Only process .mp4 files
            if not filename.endswith('.mp4'):
                continue

            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': S3_BUCKET,
                    'Key': key
                },
                ExpiresIn=expires_in
            )

            # Extract time from filename
            time_match = re.search(r'_\d{8}_(\d{6})\.mp4$', filename)
            time = time_match.group(1) if time_match else None

            result.append({
                "filename": filename,
                "download_url": url,
                "s3_key": key,
                "time": time,
                "size": obj['Size'],
                "last_modified": obj['LastModified'].isoformat(),
                "content_type": "video/mp4",
                "expires_in": expires_in
            })

        # Sort by time
        result.sort(key=lambda x: x.get("time", ""))
        return result

    except ClientError as e:
        raise RuntimeError(f"Failed to list or generate presigned URLs: {str(e)}")