# services/constellation_service.py

from skyfield.api import Topos, N, E, load_constellation_map, position_of_radec
from functools import lru_cache
from app.global_resources import ts, planets  # 전역 리소스 임포트
from app.services.timezone_conversion_service import convert_local_to_utc_time  # 시간 변환 함수 import
from app.services.sunrise_sunset_service import calculate_sunrise_sunset_for_range  # 일출 및 일몰 계산 함수 import
from datetime import datetime, timedelta

# 지구 객체 생성
earth = planets['earth']

# 별자리 데이터 로드
constellation_map = load_constellation_map()


def get_constellations_for_date_range(latitude, longitude, start_date, end_date, hour, minute):
    """
    주어진 위치와 날짜 범위에 대해 매일 특정 시간의 별자리 정보를 반환하는 함수
    일출 및 일몰 정보를 한 번의 API 호출로 가져와서 각 날짜에 대해 재사용

    Args:
        latitude (float): 위도
        longitude (float): 경도
        start_date (datetime): 시작 날짜
        end_date (datetime): 종료 날짜
        hour (int): 시간 (0-23)
        minute (int): 분 (0-59)

    Returns:
        list: 각 날짜에 대한 별자리 정보 리스트
    """
    # 요청한 날짜 범위에 대한 일출 및 일몰 정보 가져오기
    sunrise_sunset_data_list = calculate_sunrise_sunset_for_range(latitude, longitude, start_date, end_date)
    if not sunrise_sunset_data_list or "error" in sunrise_sunset_data_list[0]:
        return {"error": "Failed to calculate sunrise or sunset."}

    constellation_data = []

    # 각 날짜에 대해 반복문 수행
    for day_data in sunrise_sunset_data_list:
        try:
            date = datetime.strptime(day_data["date"], '%Y-%m-%d')
            local_datetime = datetime(date.year, date.month, date.day, hour, minute)
            offset_sec = day_data.get("offset")
            if offset_sec is None:
                return {"error": "Failed to retrieve timezone offset."}

            # 현지 시간을 UTC 시간으로 변환
            utc_datetime = convert_local_to_utc_time(local_datetime, offset_sec)

            # Skyfield에서 사용할 시간 객체 생성
            t = ts.utc(utc_datetime.year, utc_datetime.month, utc_datetime.day, utc_datetime.hour, utc_datetime.minute)
            location = Topos(latitude * N, longitude * E)  # 위치 객체 생성
            observer = earth + location  # 관측자 위치 설정
            astrometric = observer.at(t)  # 관측 시점에서의 천체 위치 계산
            ra, dec, _ = astrometric.radec()  # 적경(ra)과 적위(dec) 계산

            # 적경과 적위를 이용해 별자리를 찾기
            position = position_of_radec(ra.hours, dec.degrees)
            constellation_name = constellation_map(position)

            constellation_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "time": f"{hour:02d}:{minute:02d}",
                "constellation": constellation_name,
                "sunrise": day_data["sunrise"],
                "sunset": day_data["sunset"]
            })

        except Exception as e:
            # day_data["date"]를 사용해 오류가 발생한 날짜 정보를 가져옴
            constellation_data.append({
                "date": day_data["date"],  # 여기서 day_data["date"]를 직접 사용하여 초기화된 값을 참조
                "error": f"Failed to calculate constellation: {str(e)}"
            })

    return constellation_data


__all__ = ['get_constellations_for_date_range']
