# services/planet_opposition_service.py

from datetime import timedelta, datetime
from app.services.horizons_service import get_planet_position_from_horizons
from app.services.planet_visibility_service import calculate_planet_info
from app.services.get_timezone_info import get_timezone_info
import time


# 행성 이름과 코드 간의 매핑
def get_planet_code(planet_name):
    planet_name_map = {
        "Mercury": "Mercury",
        "Venus": "Venus",
        "Earth": "Earth",
        "Mars": "Mars barycenter",
        "Jupiter": "Jupiter barycenter",
        "Saturn": "Saturn barycenter",
        "Uranus": "Uranus barycenter",
        "Neptune": "Neptune barycenter",
        "Pluto": "Pluto barycenter"
    }
    return planet_name_map.get(planet_name)


def predict_opposition_events_with_visibility(planet_name, start_date, end_date, latitude, longitude):
    """
    특정 행성의 지구와의 대접근 이벤트 및 가시성 정보를 예측하는 함수

    Args:
        planet_name (str): 행성 이름 (예: "Mars")
        start_date (datetime): 예측을 시작할 날짜
        end_date (datetime): 예측을 종료할 날짜
        latitude (float): 관측자의 위도
        longitude (float): 관측자의 경도

    Returns:
        dict: 대접근 날짜와 관련된 정보와 가시성 정보를 포함한 딕셔너리
    """
    # 가시성 정보 먼저 계산하여 타임존 정보 확보
    visibility_info = calculate_planet_info(planet_name, latitude, longitude, start_date,
                                            range_days=(end_date - start_date).days)
    if not visibility_info or "error" in visibility_info[0]:
        return {"error": "Failed to calculate visibility"}

    timezone_id = visibility_info[0].get('timeZoneId')
    offset_sec = visibility_info[0].get('offset_sec')

    print(f"Timezone ID: {timezone_id}")

    # 행성 이름을 코드로 변환
    planet_code = get_planet_code(planet_name)
    if not planet_code:
        return {"error": f"Invalid planet name: {planet_name}"}

    print(f"planet_name 1: {planet_name}")
    print(f"planet_code 1: {planet_code}")
    current_date = start_date
    closest_date = None
    min_distance = float('inf')

    # NASA JPL Horizons API를 사용하여 주어진 범위에서의 거리 계산
    while current_date <= end_date:
        # 한 달씩 요청하기 위해 범위 설정
        month_end_date = current_date + timedelta(days=30)
        if month_end_date > end_date:
            month_end_date = end_date

        planet_data = get_planet_position_from_horizons(planet_name, current_date, (month_end_date - current_date).days)

        if "error" in planet_data:
            return {"error": "Failed to retrieve planet data from Horizons API."}

        horizons_data = planet_data.get("data")
        if not horizons_data:
            return {"error": "No valid data from Horizons API."}

        # 각 날짜의 거리 가져오기
        for day_data in horizons_data:
            delta = float(day_data["delta"])
            date = datetime.strptime(day_data["time"], "%Y-%b-%d %H:%M")

            # 가장 짧은 거리 찾기
            if delta < min_distance:
                min_distance = delta
                closest_date = date

        # 한 달씩 증가
        current_date = month_end_date + timedelta(days=1)
        time.sleep(1)  # API 요청 간 딜레이 추가

    if closest_date is None:
        return {"error": "Failed to find opposition event."}

    # closest_date를 datetime 객체로 변환하여 strftime 사용 가능하게 변경
    closest_date_str = closest_date.strftime("%Y-%m-%d")

    # 가시성 정보 데이터 정리
    visibility_data = {
        "best_time": visibility_info[0].get("best_time", "N/A"),
        "visible": visibility_info[0].get("visible", False),
        "right_ascension": visibility_info[0].get("right_ascension", "N/A"),
        "declination": visibility_info[0].get("declination", "N/A"),
        "visibility_judgment": visibility_info[0].get("visibility_judgment", "N/A")
    }

    return {
        "planet": planet_name,
        "closest_date": closest_date_str,
        "distance_to_earth": f"{min_distance:.2f} AU",
        "visibility": visibility_data,
        "timeZoneId": timezone_id,
        "offset_sec": offset_sec
    }


__all__ = ['predict_opposition_events_with_visibility']
