# services/sunrise_sunset_service.py

from datetime import datetime
from skyfield.api import Topos, N, E
from skyfield import almanac
from app.global_resources import ts, planets  # 전역 리소스 임포트


def calculate_sunrise_sunset(latitude, longitude, date):
    """
    주어진 위치(위도, 경도)와 날짜에 대한 일출 및 일몰 시간을 계산하는 함수

    Args:
        latitude (float): 위도
        longitude (float): 경도
        date (datetime): 일출 및 일몰을 계산할 날짜

    Returns:
        dict: 일출 및 일몰 시간이 포함된 딕셔너리 (UTC 기준)
    """
    location = Topos(latitude * N, longitude * E)

    # 해당 날짜의 시작 시간과 끝 시간 설정
    t0 = ts.utc(date.year, date.month, date.day)
    t1 = ts.utc(date.year, date.month, date.day, 23, 59, 59)

    # 일출 및 일몰 시간 계산
    times, events = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(planets, location))

    sunrise = None
    sunset = None
    for t, event in zip(times, events):
        if event == 0:  # 0은 일출
            sunrise = t.utc_iso()
        elif event == 1:  # 1은 일몰
            sunset = t.utc_iso()

    return {"sunrise": sunrise, "sunset": sunset}


__all__ = ['calculate_sunrise_sunset']
