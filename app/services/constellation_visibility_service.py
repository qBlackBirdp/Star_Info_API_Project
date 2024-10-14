# services/constellation_visibility_service.py

from skyfield.api import Topos, N, E, position_of_radec
from app.global_resources import ts, earth, constellation_map  # 전역 리소스 임포트
from datetime import datetime, timedelta
import numpy as np
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

# 한국 평균 고도 (고도 값 대략 100m 설정)
KOREA_AVERAGE_ALTITUDE = 450  # meters


def get_best_visibility_time_for_constellation(constellation_data, latitude, longitude, constellation_name):
    """
    주어진 날짜 범위와 위치에서 특정 별자리가 가장 잘 보이는 시간대를 계산하는 함수

    Args:
        constellation_data (list): 별자리 정보가 포함된 리스트 (일출/일몰 정보 포함)
        latitude (float): 위도
        longitude (float): 경도
        constellation_name (str): 별자리 이름

    Returns:
        list: 각 날짜에 대한 별자리의 가장 잘 보이는 시간대 정보 리스트
    """
    best_visibility_data = []

    # 각 날짜에 대해 반복문 수행
    for day_data in constellation_data:
        try:
            if "error" in day_data:
                best_visibility_data.append({
                    "date": day_data["date"],
                    "error": day_data["error"]
                })
                continue

            date = datetime.strptime(day_data["date"], '%Y-%m-%d')

            # 일몰 및 일출 시간 가져오기
            sunset_time = datetime.fromisoformat(day_data["sunset"])
            sunrise_time = datetime.fromisoformat(day_data["sunrise"])
            offset_sec = day_data.get("offset")
            if offset_sec is None:
                raise ValueError("Missing offset in day_data")
            # logging.debug(f"Date: {date}, Sunset: {sunset_time}, Sunrise: {sunrise_time}, Offset: {offset_sec}")

            # 일몰이 일출보다 늦은 경우 (다음 날로 넘어가는 경우)
            if sunset_time > sunrise_time:
                sunrise_time += timedelta(days=1)

            # Skyfield에서 사용할 위치 및 날짜 객체 생성
            location = Topos(latitude * N, longitude * E, elevation_m=KOREA_AVERAGE_ALTITUDE)
            t0 = ts.utc(sunset_time.year, sunset_time.month, sunset_time.day, sunset_time.hour,
                        sunset_time.minute)  # 일몰 시간
            t1 = ts.utc(sunrise_time.year, sunrise_time.month, sunrise_time.day, sunrise_time.hour,
                        sunrise_time.minute)  # 일출 시간

            # 일몰부터 일출까지 30분 간격으로 시간 생성
            num_steps = max(1, int((t1.tt - t0.tt) * 24 * 2))  # 30분 간격으로 시간 생성, 최소 1 스텝 보장
            times = [t0 + (t1 - t0) * frac for frac in np.linspace(0, 1, num_steps)]

            # 관측자 위치에서 천체 위치 계산
            observer = earth + location
            best_time = None
            max_altitude = -90  # 초기값은 최소 고도 설정

            for t in times:
                astrometric = observer.at(t)
                ra, dec, _ = astrometric.radec()

                # 적경과 적위를 이용해 별자리 이름을 찾음
                position = position_of_radec(ra.hours, dec.degrees)
                current_constellation = constellation_map(position)
                # logging.debug(f"Time: {t.utc_datetime()}, RA: {ra.hours}, DEC: {dec.degrees}, Constellation: {current_constellation}")

                # 주어진 별자리와 일치하는지 확인
                if current_constellation == constellation_name:
                    # 고도를 계산하여 가장 높은 고도를 가진 시간대를 찾음 (고정된 고도 사용)
                    altitude = KOREA_AVERAGE_ALTITUDE
                    # logging.debug(f"Current Altitude (Fixed): {altitude} meters")

                    if altitude > max_altitude:
                        max_altitude = altitude
                        best_time = t.utc_datetime()

            if best_time:
                # 계산된 UTC 시간을 다시 현지 시간으로 변환
                local_datetime = best_time + timedelta(seconds=offset_sec)
                logging.debug(
                    f"Best Time (UTC): {best_time}, Best Time (Local): {local_datetime}, Max Altitude: {max_altitude}")
                best_visibility_data.append({
                    "date": day_data["date"],
                    "constellation": constellation_name,
                    "best_visibility_time": local_datetime.strftime('%H:%M:%S'),
                    "max_altitude": max_altitude
                })
            else:
                best_visibility_data.append({
                    "date": day_data["date"],
                    "constellation": constellation_name,
                    "error": "Constellation not visible during the night"
                })

        except Exception as e:
            logging.error(f"Error calculating visibility for date {day_data['date']}: {str(e)}")
            best_visibility_data.append({
                "date": day_data["date"],
                "constellation": constellation_name,
                "error": f"Failed to calculate visibility: {str(e)}"
            })

    return best_visibility_data


__all__ = ['get_best_visibility_time_for_constellation']
