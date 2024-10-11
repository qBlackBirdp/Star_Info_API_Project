# services/planet_visibility_service.py

from datetime import datetime
from skyfield.api import Topos
from skyfield import almanac
from app.global_resources import ts, planets  # 전역 리소스 임포트


def calculate_planet_info(planet_name, latitude, longitude, date):
    """
    주어진 위치와 날짜에 대한 특정 행성의 가시성 및 위치 정보를 반환하는 함수

    Args:
        planet_name (str): 행성 이름 (예: "Mars")
        latitude (float): 위도
        longitude (float): 경도
        date (datetime): 가시성을 계산할 날짜

    Returns:
        dict: 행성의 가시성, 위치 정보 및 기타 세부사항을 포함한 딕셔너리
    """
    # 위치 설정
    location = Topos(latitude, longitude)

    # 천체력에서 행성 가져오기
    planet = planets[planet_name]

    # 관측 시간 설정
    t0 = ts.utc(date.year, date.month, date.day - 1, 0, 0, 0)
    t1 = ts.utc(date.year, date.month, date.day + 1, 0, 0, 0)
    times, is_visible = almanac.find_discrete(t0, t1, almanac.risings_and_settings(planets, planet, location))

    # 행성의 적경 및 적위 계산
    observer = (planets['earth'] + location).at(t0)
    astrometric = observer.observe(planet)
    ra, dec, _ = astrometric.radec()

    # 가장 좋은 관측 시간과 가시성 여부 설정
    visible = False
    best_time = None
    for t, visible_event in zip(times, is_visible):
        if visible_event == 1:  # 행성이 떠오르는 시간
            visible = True
            best_time = t.utc_datetime().time()
            break

    if best_time is None:
        best_time = "N/A"

    # 결과 반환
    return {
        "planet": planet_name,
        "date": date.strftime("%Y-%m-%d"),
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "visible": visible,
        "best_time": best_time.strftime("%H:%M") if best_time != "N/A" else best_time,
        "right_ascension": f"{ra.hours:.2f}h",  # 적경 값을 시간 단위로 변환하여 반환
        "declination": f"{dec.degrees:.2f}°"  # 적위 값을 도 단위로 반환
    }


__all__ = ['calculate_planet_info']
