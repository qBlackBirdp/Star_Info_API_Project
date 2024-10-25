# services/timezone_conversion_service.py

from datetime import datetime, timedelta
from .get_timezone_info import get_timezone_info  # 타임존 정보 가져오는 함수 import 상대경로 유지

# 캐시 딕셔너리 추가 (위도, 경도, 날짜 조합에 대해 오프셋을 저장)
utc_offset_cache = {}


def get_cached_utc_offset(latitude, longitude, timestamp):
    """
    캐시에서 UTC 오프셋을 가져오는 함수. 없으면 새로 계산.

    Args:
        latitude (float): 위도
        longitude (float): 경도
        timestamp (int): 타임스탬프

    Returns:
        tuple: (offset_sec, timezone_id)
    """
    cache_key = (latitude, longitude, timestamp)

    if cache_key in utc_offset_cache:
        return utc_offset_cache[cache_key]

    # 타임존 정보 요청
    timezone_info = get_timezone_info(latitude, longitude, timestamp)
    if 'rawOffset' not in timezone_info:
        raise ValueError("타임존 정보에 'rawOffset'이 없습니다.")

    offset_sec = timezone_info['rawOffset'] + timezone_info.get('dstOffset', 0)
    timezone_id = timezone_info['timeZoneId']

    # 캐시에 저장
    utc_offset_cache[cache_key] = (offset_sec, timezone_id)

    return offset_sec, timezone_id


def round_seconds(dt):
    """
    datetime 객체의 초 단위를 반올림하는 함수.
    """
    if dt.microsecond >= 500_000:
        dt += timedelta(seconds=1)
    return dt.replace(microsecond=0)


def convert_utc_to_local_time(utc_time, offset_sec):
    """
    주어진 UTC 시간을 현지 시간으로 변환하는 함수

    Args:
        utc_time (datetime): 변환할 UTC 시간
        offset_sec (int): 타임존 오프셋 (초 단위)

    Returns:
        datetime: 변환된 현지 시간
    """
    local_time = utc_time + timedelta(seconds=offset_sec)
    return round_seconds(local_time)  # 초 단위 반올림 후 반환


def convert_local_to_utc_time(local_time, offset_sec):
    """
    주어진 현지 시간을 UTC 시간으로 변환하는 함수

    Args:
        local_time (datetime): 변환할 현지 시간
        offset_sec (int): 타임존 오프셋 (초 단위)

    Returns:
        datetime: 변환된 UTC 시간
    """
    utc_time = local_time - timedelta(seconds=offset_sec)
    return round_seconds(utc_time)  # 초 단위 반올림 후 반환


__all__ = ['convert_utc_to_local_time', 'convert_local_to_utc_time', 'get_cached_utc_offset']
