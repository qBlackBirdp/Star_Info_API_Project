# services/moon_phase_service.py

import math
from skyfield import almanac
from datetime import datetime
from app.global_resources import ts, planets  # 전역 리소스 사용


def get_moon_phase(date):
    """
    특정 날짜의 달의 위상을 계산하고 조명율을 계산하는 함수

    Args:
        date (datetime): 달의 위상을 계산할 날짜

    Returns:
        dict: 달의 위상 정보 (0 = 뉴문, 1 = 보름달)과 조명율(0 ~ 1).
    """
    # 자정과 정오 두 번의 UTC 시간을 사용
    observation_time_midnight = ts.utc(date.year, date.month, date.day, 0)
    observation_time_noon = ts.utc(date.year, date.month, date.day, 12)

    # 자정과 정오 각각의 위상 각도 계산
    phase_angle_midnight = almanac.moon_phase(planets, observation_time_midnight)
    phase_angle_noon = almanac.moon_phase(planets, observation_time_noon)

    # 조명율 계산 (0 ~ 1 사이의 값) 두 번 계산한 뒤 평균
    illumination_midnight = (1 + math.cos(phase_angle_midnight.radians)) / 2
    illumination_noon = (1 + math.cos(phase_angle_noon.radians)) / 2
    illumination_average = (illumination_midnight + illumination_noon) / 2

    illumination = 1 - illumination_average

    # 정오 기준으로 moon_phase 반환
    phase_angle_degrees = phase_angle_noon.degrees
    if phase_angle_degrees < 0:
        phase_angle_degrees += 360
    moon_phase = phase_angle_degrees / 360.0

    return {
        "moon_phase": moon_phase,
        "phase_description": get_phase_description(moon_phase, phase_angle_degrees),
        "illumination": illumination,
        "date": date.strftime('%Y-%m-%d')
    }


def get_phase_description(moon_phase, phase_angle_degrees):
    """
    달의 위상에 따라 설명을 제공하는 함수

    Args:
        moon_phase (float): 달의 위상 (0 ~ 1).
        phase_angle_degrees (float): 위상 각도 (0 ~ 360).

    Returns:
        str: 달의 위상 설명
    """
    if 0 <= phase_angle_degrees <= 2 or 358 < phase_angle_degrees <= 360:
        return "New Moon"
    elif 2 < phase_angle_degrees <= 5 or 355 <= phase_angle_degrees <= 358:
        return "Dark Moon"  # 달이 완전히 보이지 않는 시기
    elif 5 < phase_angle_degrees < 90:
        return "Waxing Crescent"
    elif 85 <= phase_angle_degrees <= 95:
        return "First Quarter"
    elif 90 < phase_angle_degrees < 180:
        return "Waxing Gibbous"
    elif 175 <= phase_angle_degrees <= 185:
        return "Full Moon"
    elif 180 < phase_angle_degrees < 270:
        return "Waning Gibbous"
    elif 265 <= phase_angle_degrees <= 275:
        return "Last Quarter"
    elif 275 < phase_angle_degrees < 355:
        return "Waning Crescent"
    else:
        return "Unknown Phase"


def get_moon_phase_for_date(date):
    """
    특정 날짜에 대한 달의 위상을 계산하는 함수

    Args:
        date (datetime): 달의 위상을 계산할 날짜

    Returns:
        dict: 달의 위상 정보가 포함된 딕셔너리 또는 오류 메시지
    """
    try:
        # 달의 위상 계산
        moon_phase_data = get_moon_phase(date)
        return moon_phase_data

    except Exception as e:
        return {"error": f"Failed to calculate moon phase: {str(e)}"}


__all__ = ['get_moon_phase', 'get_phase_description', 'get_moon_phase_for_date']
