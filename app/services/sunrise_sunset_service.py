# services/sunrise_sunset_service.py

from datetime import datetime, timedelta
from skyfield.api import Topos, N, E
from skyfield import almanac
from app.global_resources import ts, planets  # 전역 리소스 임포트
from .timezone_conversion_service import convert_utc_to_local_time, get_cached_utc_offset  # 시간 변환 함수 import 상대경로 유지.
from .get_timezone_info import get_timezone_info  # 타임존 정보 가져오는 함수 import 상대경로 유지.
from app import cache


@cache.memoize(timeout=3600)
def calculate_sunrise_sunset_for_range(latitude, longitude, start_date, end_date, offset_sec=None, timezone_id=None):
    # print(f"[DEBUG] calculate_sunrise_sunset_for_range called with latitude: {latitude}, longitude: {longitude}, start_date: {start_date}, end_date: {end_date}")

    latitude = round(latitude, 4)
    longitude = round(longitude, 4)

    location = Topos(latitude * N, longitude * E)
    result_list = []

    # 첫 번째 날짜에 대해 타임존 오프셋을 캐싱하여 재사용
    if offset_sec is None or timezone_id is None:
        try:
            timezone_timestamp = int(start_date.timestamp())
            offset_sec, timezone_id = get_cached_utc_offset(latitude, longitude, timezone_timestamp)
            # print(f"[DEBUG] Timezone offset_sec: {offset_sec}, timezone_id: {timezone_id}")
        except Exception as e:
            print(f"[ERROR] Failed to fetch timezone info: {e}")
            return {"error": f"타임존 정보를 가져오는 데 실패했습니다: {str(e)}"}

    # 날짜 범위 내에서 일출 및 일몰 계산
    current_date = start_date
    while current_date <= end_date:
        # print(f"[DEBUG] Calculating for date: {current_date}")
        t0 = ts.utc(current_date.year, current_date.month, current_date.day - 1, 0, 0, 0)
        t1 = ts.utc(current_date.year, current_date.month, current_date.day + 1, 23, 59, 59)

        try:
            times, events = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(planets, location))
            # print(f"[DEBUG] Sunrise/Sunset times (UTC): {times}")
            # print(f"[DEBUG] Events: {events}")
        except Exception as e:
            # print(f"[ERROR] Failed to calculate sunrise/sunset for date {current_date}: {e}")
            result_list.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "error": f"Failed to calculate sunrise/sunset: {e}"
            })
            current_date += timedelta(days=1)
            continue

        sunrise_utc = None
        sunset_utc = None
        for t, event in zip(times, events):
            if event == 1 and sunrise_utc is None:
                sunrise_utc = t.utc_datetime()
            elif event == 0 and sunset_utc is None and sunrise_utc is not None:
                sunset_utc = t.utc_datetime()

        if sunrise_utc is None or sunset_utc is None:
            # print(f"[WARNING] Sunrise or sunset missing for date {current_date}")
            result_list.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "error": "일출 또는 일몰 시간을 계산할 수 없습니다."
            })
        else:
            sunrise_local = convert_utc_to_local_time(sunrise_utc, offset_sec)
            sunset_local = convert_utc_to_local_time(sunset_utc, offset_sec)
            # print(f"[DEBUG] Sunrise (local): {sunrise_local}, Sunset (local): {sunset_local}")

            result_list.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "sunrise": sunrise_local.isoformat(),
                "sunset": sunset_local.isoformat(),
                "offset": offset_sec,
                "timeZoneId": timezone_id
            })

        current_date += timedelta(days=1)

    # print(f"[DEBUG] Final sunrise/sunset result list: {result_list}")
    return result_list


@cache.memoize(timeout=3600)
def get_single_day_sunrise_sunset(latitude, longitude, date):
    """
    주어진 날짜에 대한 일출 및 일몰 데이터를 추출하는 함수

    Args:
        latitude (float): 위도
        longitude (float): 경도
        date (datetime): 일출 및 일몰을 계산할 날짜

    Returns:
        dict: 일출 및 일몰 정보가 포함된 딕셔너리 또는 오류 메시지
    """
    start_date = date
    end_date = date  # 단일 날짜이므로 시작 날짜와 종료 날짜를 동일하게 설정

    # 리스트 형태로 반환된 데이터에서 단일 날짜에 해당하는 데이터를 추출
    sunrise_sunset_data_list = calculate_sunrise_sunset_for_range(latitude, longitude, start_date, end_date, None)
    if not sunrise_sunset_data_list or "error" in sunrise_sunset_data_list[0]:
        return {"error": "Failed to calculate sunrise or sunset."}

    # 단일 날짜의 일출 및 일몰 정보 가져오기
    return sunrise_sunset_data_list[0]


__all__ = ['calculate_sunrise_sunset_for_range', 'get_single_day_sunrise_sunset']
