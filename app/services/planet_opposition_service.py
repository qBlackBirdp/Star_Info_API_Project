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


def predict_opposition_events_with_visibility(planet_name, year, latitude, longitude):
    # 4분기로 나누기
    quarter_ranges = get_quarter_ranges(year)

    events_list = []

    # 첫 분기에서 타임존 정보 한 번 호출하여 캐시
    first_quarter_start, first_quarter_end = quarter_ranges[0]
    initial_visibility_info = calculate_planet_info(planet_name, latitude, longitude, first_quarter_start,
                                                    range_days=(first_quarter_end - first_quarter_start).days)

    if not initial_visibility_info or "error" in initial_visibility_info[0]:
        logging.error(
            f"Failed to calculate visibility for {planet_name} between {first_quarter_start} and {first_quarter_end}")
        return {"error": "Failed to calculate visibility for initial quarter."}

    # 타임존 정보 캐시
    timezone_id = initial_visibility_info[0].get('timeZoneId', 'Unknown')
    offset_sec = initial_visibility_info[0].get('offset_sec', 0)

    # 각 분기에 대해 가시성 정보를 요청하고 가장 가까운 날짜 찾기
    for start_date, end_date in quarter_ranges:
        # 가시성 정보를 각 분기별로 계산 (타임존 정보는 캐시된 값을 전달)
        visibility_info = calculate_planet_info(planet_name, latitude, longitude, start_date,
                                                range_days=(end_date - start_date).days, timezone_id=timezone_id,
                                                offset_sec=offset_sec)

        # 가시성 정보가 제대로 반환되지 않으면 다음으로 넘어감
        if not visibility_info or "error" in visibility_info[0]:
            logging.error(f"Failed to calculate visibility for {planet_name} between {start_date} and {end_date}")
            continue

        # 각 분기에서 가장 가까운 날짜 데이터 찾기
        closest_event = None
        min_distance = float('inf')
        for info in visibility_info:
            if 'distance_to_earth' in info:
                distance = float(info['distance_to_earth'].split()[0])
                if distance < min_distance:
                    min_distance = distance
                    closest_event = info

        if closest_event:
            # 가장 가까운 이벤트를 리스트에 추가
            events_list.append({
                "planet": planet_name,
                "closest_date": closest_event.get("date", "N/A"),
                "distance_to_earth": f"{min_distance:.4f} AU",
                "sun_observer_target_angle": closest_event.get("sun_observer_target_angle", "N/A"),
                "visibility": {
                    "best_time": closest_event.get("best_time", "N/A"),
                    "visible": closest_event.get("visible", False),
                    "right_ascension": closest_event.get("right_ascension", "N/A"),
                    "declination": closest_event.get("declination", "N/A"),
                    "visibility_judgment": closest_event.get("visibility_judgment", "N/A")
                }
            })

    return events_list


__all__ = ['predict_opposition_events_with_visibility']
