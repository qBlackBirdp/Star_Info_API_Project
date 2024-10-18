# services/planet_opposition_service.py

from datetime import datetime
from app.services.planet_visibility_service import calculate_planet_info
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_quarter_ranges(year):
    """
    주어진 연도를 4분기로 나누어 각 분기의 시작과 끝 날짜를 반환하는 함수
    """
    return [
        (datetime(year, 1, 1), datetime(year, 3, 31)),  # Q1
        (datetime(year, 4, 1), datetime(year, 6, 30)),  # Q2
        (datetime(year, 7, 1), datetime(year, 9, 30)),  # Q3
        (datetime(year, 10, 1), datetime(year, 12, 31))  # Q4
    ]


def predict_opposition_events_with_visibility(planet_name, year, latitude, longitude, quarter=None):
    # 4분기로 나누기
    quarter_ranges = get_quarter_ranges(year)

    # 특정 분기 요청이 있는 경우 해당 분기만 사용
    if quarter:
        if quarter < 1 or quarter > 4:
            return {"error": "Invalid quarter. Please specify a value between 1 and 4."}
        quarter_ranges = [quarter_ranges[quarter - 1]]

    events_list = []

    # 첫 분기에서 타임존 정보 한 번 호출하여 캐시
    first_quarter_start, first_quarter_end = quarter_ranges[0]
    initial_visibility_info = calculate_planet_info(
        planet_name, latitude, longitude, first_quarter_start,
        range_days=(first_quarter_end - first_quarter_start).days + 1
    )

    # 타임존 정보를 얻을 수 없는 경우 오류 반환
    if not initial_visibility_info or "error" in initial_visibility_info[0]:
        return {"error": "Failed to calculate visibility for initial quarter."}

    # 타임존 정보 캐시
    timezone_info = {
        'timeZoneId': initial_visibility_info[0]['timeZoneId'],
        'offset_sec': initial_visibility_info[0]['offset_sec']
    }

    # 각 분기에 대해 가시성 정보를 요청하고 가장 가까운 날짜 찾기
    for start_date, end_date in quarter_ranges:
        visibility_info = calculate_planet_info(
            planet_name, latitude, longitude, start_date,
            range_days=(end_date - start_date).days + 1,
            timezone_info=timezone_info  # 캐시된 타임존 정보 전달
        )

        if not visibility_info or "error" in visibility_info[0]:
            continue

        # 각 분기에서 가장 가까운 날짜 3일을 찾기 위해 상위 3개의 최소 거리를 추적
        sorted_visibility_info = sorted(
            visibility_info,
            key=lambda x: float(x.get('distance_to_earth', 'inf').split()[0])
            if 'distance_to_earth' in x else float('inf')
        )

        closest_events = sorted_visibility_info[:3]  # 가장 가까운 상위 3일 선택

        for closest_event in closest_events:
            events_list.append({
                "planet": planet_name,
                "closest_date": closest_event.get("date", "N/A"),
                "distance_to_earth": closest_event.get("distance_to_earth", "N/A"),
                "sun_observer_target_angle": closest_event.get("sun_observer_target_angle", "N/A"),
                "visibility": {
                    "best_time": closest_event.get("best_time", "N/A"),
                    "visible": closest_event.get("visible", False),
                    "right_ascension": closest_event.get("right_ascension", "N/A"),
                    "declination": closest_event.get("declination", "N/A"),
                    "visibility_judgment": closest_event.get("visibility_judgment", "N/A")
                },
                "timeZoneId": timezone_info['timeZoneId'],
                "offset_sec": timezone_info['offset_sec']
            })

    return events_list if events_list else {"error": "No opposition events found for the requested quarter or year."}


__all__ = ['predict_opposition_events_with_visibility']
