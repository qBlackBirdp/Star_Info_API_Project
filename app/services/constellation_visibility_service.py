# services/constellation_visibility_service.py

from skyfield.api import Topos, N, E, Star
from app.global_resources import ts, earth  # 각종 전역 리소스 임포트
from datetime import datetime, timedelta
import numpy as np
import logging
from multiprocessing import Pool

logging.basicConfig(level=logging.DEBUG)

# 한국 평균 고도 (고도 값 대략 100m 설정)
KOREA_AVERAGE_ALTITUDE = 480  # meters


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
    constellation_name = day_data.get("constellation", "Unknown")  # try 블록 밖에서 정의
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
        times = [t0 + (t1 - t0) * frac for frac in np.linspace(0, 1, num_steps)]

        # 관찰자 위치에서 천체 위치 계산
        observer = earth + location
        best_time = None
        max_altitude = -90  # 초기값은 최소 고도 설정
        azimuth = None  # azimuth 변수를 초기화

        # 이미 가져온 적경(ra)과 적위(dec) 사용
        ra_deg = day_data.get("ra_deg")
        dec_deg = day_data.get("dec_deg")
        if ra_deg is None or dec_deg is None:
            raise ValueError(f"Missing RA or DEC for constellation {constellation_name}")

        # 별자리 정보를 Star 객체로 변환
        star = Star(ra_hours=ra_deg / 15, dec_degrees=dec_deg)

        for t in times:
            astrometric = observer.at(t).observe(star).apparent()
            alt, az, _ = astrometric.altaz()
            altitude = alt.degrees
            azimuth = az.degrees

            # 고도가 음수이면 해당 시간은 무시
            if altitude < 0:
                continue

            # 고도를 계산해서 가장 높은 고도를 가진 시간대를 찾음
            if altitude > max_altitude:
                max_altitude = altitude
                best_time = t.utc_datetime()

        if best_time:
            # 계산된 UTC 시간을 다시 현지 시간으로 변환
            local_datetime = best_time + timedelta(seconds=offset_sec)

            # 고도와 일출/일몰 시간에 따른 visibility_judgment 설정
            if best_time > sunset_time or best_time < sunrise_time:
                # 일몰 이후 또는 일출 이전이라면
                if max_altitude >= 30:  # 기준 고도를 30도로 낮춤
                    visibility_judgment = "Good visibility - The constellation is high in the sky and it's dark enough for easy observation."
                else:
                    visibility_judgment = "Difficult to observe - The constellation is visible, but it is low in the sky, making it harder to see."
            else:
                # 일출 이후 일몰 이전
                if max_altitude >= 30:
                    visibility_judgment = "Difficult to observe - The constellation is high, but daylight might make it challenging to see."
                else:
                    visibility_judgment = "Not recommended - The constellation is low in the sky and daylight makes it very hard to observe."

            # 방위경을 동서남북 분포로 변환
            direction = "Unknown"
            if azimuth is not None:
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
                "azimuth": direction,
                "visibility_judgment": visibility_judgment
            }
        else:
            return {
                "date": day_data["date"],
                "constellation": constellation_name,
                "error": "Constellation not visible during the night"
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
        results = pool.starmap(process_day_data, [(day, latitude, longitude) for day in constellation_data])
    return results


__all__ = ['calculate_visibility_for_constellations_parallel']
