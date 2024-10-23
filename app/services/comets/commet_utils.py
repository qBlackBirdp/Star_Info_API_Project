# commet_utils.py
from datetime import datetime

from app.global_resources import ts, load, earth
from skyfield.api import Topos, Star
from math import radians


def parse_ra_dec(ra_str, dec_str):
    # 적경(RA) 변환 (시간:분:초 -> 시간 단위)
    ra_h, ra_m, ra_s = map(float, ra_str.split())
    ra_hours = ra_h + (ra_m / 60) + (ra_s / 3600)  # 시간각으로 변환

    # 적위(Dec) 변환 (도:분:초 -> 도 단위)
    dec_sign = 1 if dec_str[0] == '+' else -1
    dec_d, dec_m, dec_s = map(float, dec_str[1:].split())
    dec_degrees = dec_sign * (dec_d + (dec_m / 60) + (dec_s / 3600))

    return ra_hours, dec_degrees


def calculate_altitude(ra_str, dec_str, delta, latitude, longitude, elevation, approach_time):
    # 적경(RA)과 적위(Dec)를 문자열에서 변환
    ra_hours, dec_degrees = parse_ra_dec(ra_str, dec_str)
    print(f"Converted RA (hours): {ra_hours}, Converted Dec (degrees): {dec_degrees}")

    # 관측자의 위치 설정 (고도 포함)
    observer_location = Topos(latitude_degrees=latitude, longitude_degrees=longitude, elevation_m=elevation)
    print(f"Observer Location: {observer_location}")

    # 혜성의 적경(RA), 적위(Dec)를 Star 객체로 변환
    comet_position = Star(ra_hours=ra_hours, dec_degrees=dec_degrees)
    print(f"Comet Position (Star): {comet_position}")

    # 지구와 관측자 위치를 설정해 관측 시점 설정
    observer = earth + observer_location

    # 지구에서 혜성의 위치를 관측
    astrometric = observer.at(ts.utc(approach_time.year, approach_time.month, approach_time.day,
                                     approach_time.hour, approach_time.minute)).observe(comet_position).apparent()

    # 고도와 방위각을 계산할 때 관측자의 위치를 명시적으로 제공
    alt, az, distance = astrometric.altaz()

    # 고도 값 반환
    return alt.degrees


def analyze_comet_data(data):
    """
    혜성 접근 이벤트 데이터를 정리하고 분석하는 함수.

    Args:
        data (list): 혜성 접근 이벤트 데이터 리스트.

    Returns:
        dict: 분석된 접근 이벤트 정보.
    """
    try:
        if not data:
            return {"error": "No data available for analysis."}

        # 접근 이벤트를 시간 순으로 정렬
        sorted_data = sorted(data, key=lambda x: datetime.strptime(x['time'], '%Y-%b-%d %H:%M'))

        if not sorted_data:
            return {"error": "Sorted data is empty."}

        # 지구와 가장 가까운 접근 이벤트 찾기
        closest_approach = min(sorted_data, key=lambda x: float(x['delta']))

        # 가장 가까운 접근 이벤트 반환
        return {"closest_approach": closest_approach}
    except Exception as e:
        return {"error": f"Failed to analyze comet data: {str(e)}"}


def analyze_comet_data_for_approach(data):
    """
    혜성 접근 데이터를 분석하여 접근 및 멀어짐의 변화를 감지하는 함수.
    여러 접근 이벤트를 분석하여 혜성이 다시 가까워지는 시점을 찾는다.
    """
    try:
        if not data:
            return {"error": "No data available for analysis."}

        sorted_data = sorted(data, key=lambda x: datetime.strptime(x['time'], '%Y-%b-%d %H:%M'))
        if not sorted_data:
            return {"error": "Sorted data is empty."}

        closest_approach = min(sorted_data, key=lambda x: float(x['delta']))

        # 멀어지고 있다면 이후 다시 가까워지는 시점을 찾기
        deldot = float(closest_approach['deldot'])
        if deldot > 0:  # 현재 멀어지고 있는 경우
            for event in sorted_data:
                if float(event['deldot']) < 0:  # 다시 가까워지는 시점
                    return {"closest_approach": event, "message": "Comet is getting closer again."}

        return {"closest_approach": closest_approach}
    except Exception as e:
        return {"error": f"Failed to analyze comet data: {str(e)}"}


__all__ = ['analyze_comet_data', 'parse_ra_dec']
