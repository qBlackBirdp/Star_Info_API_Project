# services/timezone_conversion_service.py

from datetime import datetime, timedelta


def convert_utc_to_local_time(utc_time, offset_sec):
    """
    주어진 UTC 시간을 현지 시간으로 변환하는 함수

    Args:
        utc_time (datetime): 변환할 UTC 시간
        offset_sec (int): 타임존 오프셋 (초 단위)

    Returns:
        datetime: 변환된 현지 시간
    """
    return utc_time + timedelta(seconds=offset_sec)


__all__ = ['convert_utc_to_local_time']
