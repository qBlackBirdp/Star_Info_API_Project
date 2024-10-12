# services/sunrise_sunset_service.py

from datetime import datetime, timedelta
from skyfield.api import Topos, N, E
from skyfield import almanac
from app.global_resources import ts, planets  # 전역 리소스 임포트
from .timezone_conversion_service import convert_utc_to_local_time  # 시간 변환 함수 import 상대경로 유지.
from .get_timezone_info import get_timezone_info  # 타임존 정보 가져오는 함수 import 상대경로 유지.


def calculate_sunrise_sunset(latitude, longitude, date, cached_sunrise_sunset=None):
    """
    주어진 위치(위도, 경도)와 날짜에 대한 일출 및 일몰 시간을 계산하는 함수 (현지 시간 기준)

    Args:
        latitude (float): 위도
        longitude (float): 경도
        date (datetime): 일출 및 일몰을 계산할 날짜
        cached_sunrise_sunset (dict, optional): 캐싱된 일출 및 일몰 정보

    Returns:
        dict: 일출 및 일몰 시간이 포함된 딕셔너리 (현지 시간 기준)
    """
    # 사용자가 요청한 경우 캐시된 데이터 반환
    if cached_sunrise_sunset is not None:
        return cached_sunrise_sunset

    location = Topos(latitude * N, longitude * E)

    # 해당 날짜의 일출과 일몰을 찾기 위해 전날 자정부터 다음 날 자정까지 범위 설정
    t0 = ts.utc(date.year, date.month, date.day - 1, 0, 0, 0)  # 전날 자정 (UTC 기준)
    t1 = ts.utc(date.year, date.month, date.day + 1, 23, 59, 59)  # 다다음 날 자정 직전까지

    # 일출 및 일몰 시간 계산 (UTC 기준)
    times, events = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(planets, location))

    sunrise_utc = None
    sunset_utc = None
    for t, event in zip(times, events):
        if event == 1 and sunrise_utc is None:  # 1은 일출
            sunrise_utc = t.utc_datetime()
        elif event == 0 and sunset_utc is None and sunrise_utc is not None:  # 0은 일몰, 일출 후에만 일몰을 설정
            sunset_utc = t.utc_datetime()

    if sunrise_utc is None or sunset_utc is None:
        return {"error": "일출 또는 일몰 시간을 계산할 수 없습니다."}

    # Google Time Zone API를 사용하여 타임존 정보 가져오기 (한 번만 호출하여 재사용)
    try:
        timezone_timestamp = int(sunrise_utc.timestamp())  # 일출 시간을 기준으로 타임존 정보 호출
        timezone_info = get_timezone_info(latitude, longitude, timezone_timestamp)
        print("Time Zone API Response:", timezone_info)  # 응답 내용 출력
        if 'rawOffset' not in timezone_info:
            raise ValueError("타임존 정보에 'rawOffset'이 없습니다.")
        offset_sec = timezone_info['rawOffset'] + timezone_info.get('dstOffset', 0)
    except Exception as e:
        return {"error": f"타임존 정보를 가져오는 데 실패했습니다: {str(e)}"}

    # UTC 시간 -> 현지 시간으로 변환 (timezone_conversion_service 사용)
    sunrise_local = convert_utc_to_local_time(sunrise_utc, offset_sec)
    sunset_local = convert_utc_to_local_time(sunset_utc, offset_sec)

    result = {
        "sunrise": sunrise_local.isoformat(),
        "sunset": sunset_local.isoformat(),
    }

    return result


__all__ = ['calculate_sunrise_sunset']