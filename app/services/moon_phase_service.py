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
    # 하루 동안 여덟 개의 UTC 시간을 사용 (3시간 간격)
    observation_times = [
        ts.utc(date.year, date.month, date.day, 0),
        ts.utc(date.year, date.month, date.day, 3),
        ts.utc(date.year, date.month, date.day, 6),
        ts.utc(date.year, date.month, date.day, 9),
        ts.utc(date.year, date.month, date.day, 12),
        ts.utc(date.year, date.month, date.day, 15),
        ts.utc(date.year, date.month, date.day, 18),
        ts.utc(date.year, date.month, date.day, 21)
    ]

    # 여덟 시점 각각의 위상 각도와 조명률 계산
    phase_angles = [almanac.moon_phase(planets, t) for t in observation_times]
    illuminations = [(1 + math.cos(angle.radians)) / 2 for angle in phase_angles]

    # 조명율 평균 계산
    illumination_average = sum(illuminations) / len(illuminations)
    illumination = 1 - illumination_average

    # moon_phase를 여덟 시점의 평균 위상 각도로 계산
    phase_angle_average = sum(angle.degrees for angle in phase_angles) / len(phase_angles)
    if phase_angle_average < 0:
        phase_angle_average += 360
    moon_phase = phase_angle_average / 360.0

    return {
        "moon_phase": moon_phase,
        "phase_description": get_phase_description(moon_phase, phase_angle_average, illumination),
        "illumination": illumination,
        "date": date.strftime('%Y-%m-%d')
    }


def get_phase_description(moon_phase, phase_angle_degrees, illumination):
    """
    달의 위상에 따라 설명을 제공하는 함수

    Args:
        moon_phase (float): 달의 위상 (0 ~ 1).
        phase_angle_degrees (float): 위상 각도 (0 ~ 360).
        illumination (float): 달의 조명률 (0 ~ 1).

    Returns:
        str: 달의 위상 설명
    """
    # 조명률이 0.98 이상이면 보름달로 강제 설정
    if illumination >= 0.99:
        return "Full Moon"

    if 0 <= phase_angle_degrees <= 5 or 355 < phase_angle_degrees <= 360:
        return "New Moon"
    elif 5 < phase_angle_degrees <= 10 or 350 <= phase_angle_degrees <= 355:
        return "Dark Moon"  # 달이 거의 완전히 보이지 않는 시기
    elif 10 < phase_angle_degrees < 85:
        return "Waxing Crescent"
    elif 85 <= phase_angle_degrees <= 95:
        return "First Quarter"
    elif 95 < phase_angle_degrees < 175:
        return "Waxing Gibbous"
    elif 170 <= phase_angle_degrees <= 190:
        return "Full Moon"
    elif 190 < phase_angle_degrees < 265:
        return "Waning Gibbous"
    elif 265 <= phase_angle_degrees <= 275:
        return "Last Quarter"
    elif 275 < phase_angle_degrees < 350:
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
