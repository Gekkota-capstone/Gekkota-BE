# /util/scheduler.py

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, Any
from pytz import timezone

logger = logging.getLogger(__name__)

# 한국 시간대 설정
KST = timezone('Asia/Seoul')


def get_kst_now():
    """현재 한국 시간 반환"""
    return datetime.now(KST)


def get_time_range_for_schedule():
    """
    현재 시간 기준으로 처리할 시간 범위 반환
    현재 시간이 15:23이면 -> 15:22~15:23 처리
    현재 시간이 15:37이면 -> 15:36~15:37 처리
    매 1분마다 실행되는 것을 가정
    """
    now = get_kst_now()

    # 1분 단위로 계산
    end_time = now.replace(second=0, microsecond=0)
    start_time = end_time - timedelta(minutes=1)

    logger.info(f"Processing data for time range: {start_time} to {end_time}")

    return start_time, end_time


async def run_every_5_minutes(func: Callable, *args, **kwargs):
    """
    1분마다 함수를 실행하는 비동기 루프로 변경
    정각 기준으로 정확히 매 분마다 실행
    """
    while True:
        # 현재 시간
        now = datetime.now()

        # 다음 1분 간격 계산
        next_minute = now.minute + 1
        next_time = now.replace(minute=next_minute % 60, second=0, microsecond=0)

        # 시간이 넘어가는 경우 처리
        if next_minute >= 60:
            next_time = next_time.replace(hour=(now.hour + 1) % 24)
            # 날짜가 넘어가는 경우 처리
            if next_time.hour < now.hour:
                next_time = next_time + timedelta(days=1)

        # 다음 실행 시간까지 대기
        sleep_seconds = (next_time - now).total_seconds()
        logger.info(
            f"Next scheduled task at {next_time.strftime('%Y-%m-%d %H:%M:%S')} (in {sleep_seconds:.0f} seconds)")
        await asyncio.sleep(sleep_seconds)

        # 함수 실행
        try:
            now_execution = datetime.now()
            logger.info(f"Starting scheduled task at {now_execution.strftime('%Y-%m-%d %H:%M:%S')}")

            # 시간 범위 계산
            start_time, end_time = get_time_range_for_schedule()

            # 시간 범위를 추가 인자로 전달
            task_kwargs = dict(kwargs)
            task_kwargs.update({
                "start_time": start_time,
                "end_time": end_time
            })

            if asyncio.iscoroutinefunction(func):
                await func(*args, **task_kwargs)
            else:
                func(*args, **task_kwargs)

            logger.info(
                f"Completed scheduled task. Duration: {(datetime.now() - now_execution).total_seconds():.2f} seconds")
        except Exception as e:
            logger.error(f"Error during scheduled execution: {str(e)}")


async def run_daily_at_midnight(func: Callable, *args, **kwargs):
    """
    매일 자정에 함수를 실행하는 비동기 루프
    한국 시간 기준 (UTC+9)
    """
    while True:
        # 현재 한국 시간
        now = get_kst_now()

        # 다음 자정 계산
        next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now.hour != 0 or now.minute != 0 or now.second != 0:
            next_midnight = next_midnight + timedelta(days=1)

        # 다음 자정까지 대기
        sleep_seconds = (next_midnight - now).total_seconds()
        logger.info(
            f"Next daily task scheduled at {next_midnight.strftime('%Y-%m-%d %H:%M:%S')} (in {sleep_seconds:.0f} seconds)")
        await asyncio.sleep(sleep_seconds)

        # 함수 실행
        try:
            now_execution = get_kst_now()
            logger.info(f"Starting daily task at {now_execution.strftime('%Y-%m-%d %H:%M:%S')}")

            if asyncio.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)

            logger.info(
                f"Completed daily task. Duration: {(get_kst_now() - now_execution).total_seconds():.2f} seconds")
        except Exception as e:
            logger.error(f"Error during daily execution: {str(e)}")