# services/moon_phase_service.py

from datetime import datetime, timedelta
from app.global_resources import ts, earth, sun, moon  # 전역 리소스 사용
from .timezone_conversion_service import convert_utc_to_local_time  # UTC -> 현지 시간 변환
from .get_timezone_info import get_timezone_info  # 타임존 정보 가져오는 함수 import 상대경로 유지.


def get_moon_phase(local_time, utc_offset_sec):
    """
    특정 날짜의 달의 위상을 계산하는 함수 (UTC 오프셋 사용)

    Args:
        local_time (datetime): 현지 시각.
        utc_offset_sec (int): UTC 오프셋 (초 단위).

    Returns:
        dict: 달의 위상 정보 (0 = 뉴문, 1 = 보름달).
    """
    # 현지 시각을 UTC로 변환
    utc_time = local_time - timedelta(seconds=utc_offset_sec)

    # Skyfield에서 사용하는 Time 객체로 변환
    observation_time = ts.utc(utc_time.year, utc_time.month, utc_time.day, utc_time.hour, utc_time.minute)

    # 지구에서 본 달과 태양의 위치
    astrometric_moon = earth.at(observation_time).observe(moon)
    astrometric_sun = earth.at(observation_time).observe(sun)

    # 달과 태양의 위상각 차이 계산 (0 = 뉴문, 180 = 보름달)
    phase_angle = astrometric_moon.separation_from(astrometric_sun).degrees

    # 위상 비율 계산 (0 = 뉴문, 1 = 보름달)
    moon_phase = (1 - abs(phase_angle - 180) / 180)

    return {
        "moon_phase": moon_phase,
        "phase_description": get_phase_description(moon_phase)
    }


def get_phase_description(moon_phase):
    """
    달의 위상에 따라 설명을 제공하는 함수

    Args:
        moon_phase (float): 달의 위상 (0 ~ 1).

    Returns:
        str: 달의 위상 설명
    """
    if moon_phase == 0:
        return "New Moon"
    elif 0 < moon_phase < 0.25:
        return "Waxing Crescent"
    elif moon_phase == 0.25:
        return "First Quarter"
    elif 0.25 < moon_phase < 0.5:
        return "Waxing Gibbous"
    elif moon_phase == 0.5:
        return "Full Moon"
    elif 0.5 < moon_phase < 0.75:
        return "Waning Gibbous"
    elif moon_phase == 0.75:
        return "Last Quarter"
    elif 0.75 < moon_phase < 1:
        return "Waning Crescent"
    else:
        return "Unknown Phase"


def get_moon_phase_for_date(latitude, longitude, date):
    """
    특정 날짜에 대한 달의 위상을 계산하는 함수 (현지 시간 기준)

    Args:
        latitude (float): 위도
        longitude (float): 경도
        date (datetime): 달의 위상을 계산할 날짜

    Returns:
        dict: 달의 위상 정보가 포함된 딕셔너리 또는 오류 메시지
    """
    try:
        # 타임존 정보 가져오기
        timezone_timestamp = int(date.timestamp())
        timezone_info = get_timezone_info(latitude, longitude, timezone_timestamp)
        if 'rawOffset' not in timezone_info:
            raise ValueError("타임존 정보에 'rawOffset'이 없습니다.")
        offset_sec = timezone_info['rawOffset'] + timezone_info.get('dstOffset', 0)

        # 달의 위상 계산
        moon_phase_data = get_moon_phase(date, offset_sec)
        return moon_phase_data

    except Exception as e:
        return {"error": f"Failed to calculate moon phase: {str(e)}"}


# __all__ = ['get_moon_phase', 'get_phase_description', 'get_moon_phase_for_date']
