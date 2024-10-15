# services/planet_visibility_service.py

from datetime import datetime, timedelta
from skyfield.api import Topos
from skyfield import almanac
from app.global_resources import ts, planets  # 전역 리소스 임포트
from app.services.timezone_conversion_service import convert_utc_to_local_time  # 시간 변환 함수 import
from app.services.sunrise_sunset_service import calculate_sunrise_sunset_for_range  # 일출 및 일몰 계산 함수 import
from app.services.horizons_service import get_planet_position_from_horizons  # NASA JPL Horizons API 데이터 호출 함수 import


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


def calculate_planet_info(planet_name, latitude, longitude, date, range_days=1):
    """
    주어진 위치와 날짜에 대한 특정 행성의 가시성 및 위치 정보를 반환하는 함수

    Args:
        planet_name (str): 행성 이름 (예: "Mars")
        latitude (float): 위도
        longitude (float): 경도
        date (datetime): 가시성을 계산할 날짜
        range_days (int): 날짜 범위 (기본값: 1일)

    Returns:
        list: 행성의 가시성, 위치 정보 및 기타 세부사항을 포함한 딕셔너리 리스트
    """
    print(f"planet_name: {planet_name}")
    # 위치 설정
    location = Topos(latitude, longitude)

    # 지정된 범위에 대한 일출 및 일몰 정보 가져오기
    end_date = date + timedelta(days=range_days - 1)
    sunrise_sunset_data_list = calculate_sunrise_sunset_for_range(latitude, longitude, date, end_date)

    if not sunrise_sunset_data_list or "error" in sunrise_sunset_data_list[0]:
        return [{"error": "Failed to calculate sunrise or sunset."}]

    # NASA JPL Horizons API를 사용하여 행성 데이터 가져오기
    planet_data = get_planet_position_from_horizons(planet_name, date, range_days)
    if "error" in planet_data:
        return [{"error": "Failed to retrieve planet data from Horizons API."}]

    # 파싱된 Horizons 데이터 추가
    horizons_data = planet_data.get("data")
    if not horizons_data:
        return [{"error": "No valid data from Horizons API."}]

    # 행성 이름을 코드로 변환
    planet_code = get_planet_code(planet_name)
    if not planet_code:
        print(f"planet_code: {planet_code}")
        return [{"error": f"Invalid planet name: {planet_name}"}]

    results = []

    for closest_data, sunrise_sunset_data in zip(horizons_data, sunrise_sunset_data_list):
        delta = float(closest_data["delta"])
        s_o_t = float(closest_data["s-o-t"])
        current_date = datetime.strptime(closest_data["time"], "%Y-%b-%d %H:%M")

        # 로그 추가: 반복문 안에서의 날짜 출력
        print(f"Current date in loop: {current_date}")

        # 타임존 오프셋 및 일출, 일몰 시간 가져오기
        offset_sec = sunrise_sunset_data.get("offset")
        if offset_sec is None:
            results.append({"error": "Failed to retrieve timezone offset."})
            continue

        sunrise_time = datetime.fromisoformat(sunrise_sunset_data["sunrise"]).time()
        if sunrise_time is None:
            results.append({"error": "Failed to retrieve sunrise_time."})
            continue

        sunset_time = datetime.fromisoformat(sunrise_sunset_data["sunset"]).time()

        # 천체력에서 행성 가져오기
        planet = planets[planet_code]

        # 관측 시간 설정
        t0 = ts.utc(current_date.year, current_date.month, current_date.day - 1, 0, 0, 0)
        t1 = ts.utc(current_date.year, current_date.month, current_date.day + 1, 0, 0, 0)
        times, is_visible = almanac.find_discrete(t0, t1, almanac.risings_and_settings(planets, planet, location))

        # 행성의 적경 및 적위 계산
        observer = (planets['earth'] + location).at(
            ts.utc(current_date.year, current_date.month, current_date.day, 0, 0, 0))
        astrometric = observer.observe(planet)
        ra, dec, _ = astrometric.radec()

        # 가시성 판단 추가 로직
        visibility_judgment = "Unknown"
        if delta < 1.5 and s_o_t > 30:
            visibility_judgment = "Good visibility"
        elif 1.5 <= delta < 2.5 and s_o_t > 20:
            visibility_judgment = "Moderate visibility"
        else:
            visibility_judgment = "Poor visibility"

        # 가장 좋은 관측 시간과 가시성 여부 설정
        visible = False
        best_time = None
        for t, visible_event in zip(times, is_visible):
            if visible_event == 1:  # 행성이 떠오르는 시간
                visible = True
                best_time = convert_utc_to_local_time(t.utc_datetime(), offset_sec).time()

                # 낮 시간대인지 여부 판별
                if sunrise_time <= best_time <= sunset_time:
                    visible = False
                    best_time = "낮 시간대 (관측 불가)"
                break

        if best_time is None:
            best_time = "N/A"

        # 결과 추가
        results.append({
            "planet": planet_name,
            "date": closest_data["time"].split()[0],
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "visible": visible,
            "best_time": best_time if isinstance(best_time, str) else best_time.strftime("%H:%M"),
            "right_ascension": f"{ra.hours:.2f}h",  # 적경 값을 시간 단위로 변환하여 반환
            "declination": f"{dec.degrees:.2f}°",  # 적위 값을 도 단위로 반환
            "distance_to_earth": f"{delta:.2f} AU",  # 지구와의 거리 추가
            "sun_observer_target_angle": f"{s_o_t:.2f}°",  # 태양-관측자-행성 각도 추가
            "visibility_judgment": visibility_judgment  # 가시성 판단 추가
        })

    return results
