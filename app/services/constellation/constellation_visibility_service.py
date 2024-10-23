# services/constellation_visibility_service.py

from skyfield.api import Topos, N, E, Star
from app.global_resources import ts, earth  # 각종 전역 리소스 임포트
from datetime import datetime, timedelta
import numpy as np
import logging
from multiprocessing import Pool
from functools import lru_cache

logging.basicConfig(level=logging.DEBUG)

# 한국 평균 고도 (고도 값 대략 100m 설정)
KOREA_AVERAGE_ALTITUDE = 480  # meters


# 캐시 적용: 별자리 가시성 정보를 캐싱하여 중복 계산을 방지
@lru_cache(maxsize=128)
def process_day_data_cached(day_data_tuple, latitude, longitude):
    day_data = dict(day_data_tuple)  # 튜플을 딕셔너리로 변환
    return process_day_data(day_data, latitude, longitude)


def process_day_data(day_data, latitude, longitude):
    """
    주어진 날짜와 위치에서 특정 별자리가 가장 잘 보인다고 예상되는 시간대를 계산하는 함수

    Args:
        day_data (dict): 별자리 정보가 포함된 딕셔너리 (일출/일몰 정보 포함)
        latitude (float): 위도
        longitude (float): 경도

    Returns:
        dict: 별자리의 가장 잘 보인다고 예상되는 시간대 정보
    """
    constellation_name = day_data.get("constellation", "Unknown")
    try:
        if "error" in day_data:
            return {
                "date": day_data["date"],
                "error": day_data["error"]
            }

        date = datetime.strptime(day_data["date"], '%Y-%m-%d')

        # 일몰 및 일출 시간 가져오기
        sunset_time = datetime.fromisoformat(day_data["sunset"])
        sunrise_time = datetime.fromisoformat(day_data["sunrise"])
        offset_sec = day_data.get("offset")
        if offset_sec is None:
            raise ValueError("Missing offset in day_data")

        # 일몰이 일출보다 늦은 경우 (다음 날로 넘어가는 경우)
        if sunset_time > sunrise_time:
            sunrise_time += timedelta(days=1)

        # Skyfield에서 사용할 위치 및 날짜 객체 생성
        location = Topos(latitude * N, longitude * E, elevation_m=KOREA_AVERAGE_ALTITUDE)
        t0 = ts.utc(sunset_time.year, sunset_time.month, sunset_time.day, sunset_time.hour, sunset_time.minute)
        t1 = ts.utc(sunrise_time.year, sunrise_time.month, sunrise_time.day, sunrise_time.hour, sunrise_time.minute)

        # 일몰부터 일출까지 10분 간격으로 시간 생성 (간격 조정)
        num_steps = max(1, int((t1.tt - t0.tt) * 24 * 6))  # 10분 간격으로 시간 생성, 최소 1 스텝 보장
        times = ts.utc([t0.utc_datetime() + timedelta(minutes=10 * i) for i in range(num_steps)])

        # 관찰자 위치에서 천체 위치 계산 (벡터화 적용)
        observer = earth + location

        # 이미 가져온 적경(ra)과 적위(dec) 사용
        ra_deg = day_data.get("ra_deg")
        dec_deg = day_data.get("dec_deg")
        if ra_deg is None or dec_deg is None:
            raise ValueError(f"Missing RA or DEC for constellation {constellation_name}")

        # 별자리 정보를 Star 객체로 변환
        star = Star(ra_hours=ra_deg / 15, dec_degrees=dec_deg)

        # 천체 위치 계산 (벡터화 처리)
        astrometric = observer.at(times).observe(star).apparent()
        altitudes, azimuths, _ = astrometric.altaz()

        # Lazy Evaluation 적용: 최고 고도 찾기
        max_altitude = max(altitudes.degrees)
        if max_altitude < 0:
            # 모든 고도가 음수인 경우 (관측 불가)
            return {
                "date": day_data["date"],
                "constellation": constellation_name,
                "error": "Constellation not visible during the night"
            }

        # 최고 고도 시간 찾기
        best_index = np.argmax(altitudes.degrees)
        best_time = times[best_index].utc_datetime()

        # 계산된 UTC 시간을 다시 현지 시간으로 변환
        local_datetime = best_time + timedelta(seconds=offset_sec)

        # 방위경을 동서남북 분포로 변환
        azimuth = azimuths.degrees[best_index]
        direction = "Unknown"
        if 0 <= azimuth < 22.5 or 337.5 <= azimuth <= 360:
            direction = "North"
        elif 22.5 <= azimuth < 67.5:
            direction = "Northeast"
        elif 67.5 <= azimuth < 112.5:
            direction = "East"
        elif 112.5 <= azimuth < 157.5:
            direction = "Southeast"
        elif 157.5 <= azimuth < 202.5:
            direction = "South"
        elif 202.5 <= azimuth < 247.5:
            direction = "Southwest"
        elif 247.5 <= azimuth < 292.5:
            direction = "West"
        elif 292.5 <= azimuth < 337.5:
            direction = "Northwest"

        return {
            "date": day_data["date"],
            "constellation": constellation_name,
            "best_visibility_time": local_datetime.strftime('%H:%M:%S'),
            "max_altitude": f"{max_altitude:.2f}°",
            "azimuth": direction
        }

    except Exception as e:
        return {
            "date": day_data["date"],
            "constellation": constellation_name,
            "error": f"Failed to calculate visibility: {str(e)}"
        }


def calculate_visibility_for_constellations_parallel(constellation_data, latitude, longitude):
    """
    별자리 데이터에 대한 최적 가시성 정보를 병렬 처리로 계산하는 함수

    Args:
        constellation_data (list): 별자리 정보 리스트
        latitude (float): 위도
        longitude (float): 경도

    Returns:
        list: 가시성 정보가 추가된 별자리 정보 리스트
    """
    with Pool() as pool:
        results = pool.starmap(process_day_data_cached,
                               [(tuple(day.items()), latitude, longitude) for day in constellation_data])
    return results


__all__ = ['calculate_visibility_for_constellations_parallel']
