# services/timezone_conversion_service.py

from datetime import datetime, timedelta


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


__all__ = ['convert_utc_to_local_time', 'convert_local_to_utc_time']
