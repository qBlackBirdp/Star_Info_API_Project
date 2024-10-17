# services/planet_opposition_service.py

from datetime import datetime
from app.services.horizons_service import get_planet_position_from_horizons
from app.services.planet_visibility_service import calculate_planet_info
from global_db_connection import get_db_connection


# 행성 이름과 코드 간의 매핑
def get_planet_code(planet_name):
    planet_name_map = {
        "Mercury": 199,
        "Venus": 299,
        "Earth": 399,
        "Mars": 499,
        "Jupiter": 599,
        "Saturn": 699,
        "Uranus": 799,
        "Neptune": 899,
        "Pluto": 999
    }
    return planet_name_map.get(planet_name)


def predict_opposition_events_with_visibility(planet_name, start_date, end_date, latitude, longitude):
    """
    특정 행성의 지구와의 대접근 이벤트 및 가시성 정보를 예측하는 함수

    Args:
        planet_name (str): 행성 이름 (예: "Mars")
        start_date (datetime): 예측을 시작할 날짜
        end_date (datetime): 예측을 종료할 날짜
        latitude (float): 관측자의 위도
        longitude (float): 관측자의 경도

    Returns:
        dict: 대접근 날짜와 관련된 정보와 가시성 정보를 포함한 딕셔너리
    """
    # 가시성 정보 먼저 계산하여 타임존 정보 확보
    visibility_info = calculate_planet_info(planet_name, latitude, longitude, start_date,
                                            range_days=(end_date - start_date).days)
    if not visibility_info or "error" in visibility_info[0]:
        return {"error": "Failed to calculate visibility"}

    timezone_id = visibility_info[0].get('timeZoneId')
    offset_sec = visibility_info[0].get('offset_sec')

    # 행성 이름을 코드로 변환
    planet_code = get_planet_code(planet_name)
    if not planet_code:
        return {"error": f"Invalid planet name: {planet_name}"}

    # 전역 DB 연결 가져오기
    conn = get_db_connection()
    if conn is None:
        return {"error": "DB 연결을 사용할 수 없습니다."}

    cursor = None
    try:
        cursor = conn.cursor()
        # 행성 데이터가 이미 DB에 존재하는지 확인
        table_name = f"{planet_name.lower()}_{start_date.year}_opposition_events"  # 여기서만 소문자로 변환
        select_query = f"""
            SELECT reg_date, distance FROM {table_name}
            WHERE planet_code = %s AND reg_date BETWEEN %s AND %s
        """
        cursor.execute(select_query, (planet_code, start_date, end_date))
        rows = cursor.fetchall()

        closest_date = None
        min_distance = float('inf')

        if rows:
            # DB에서 데이터를 가져와서 가장 가까운 거리 계산
            for row in rows:
                reg_date, delta = row
                if delta < min_distance:
                    min_distance = delta
                    closest_date = reg_date
        else:
            # 해당 연도와 행성의 데이터가 없는 경우 Horizons API 요청
            year_start_date = datetime(start_date.year, 1, 1)
            year_end_date = datetime(start_date.year, 12, 31)

            planet_data = get_planet_position_from_horizons(planet_name, year_start_date,
                                                            (year_end_date - year_start_date).days)

            if "error" in planet_data:
                return {"error": "Failed to retrieve planet data from Horizons API."}

            horizons_data = planet_data.get("data")
            if not horizons_data:
                return {"error": "No valid data from Horizons API."}

            # 각 날짜의 거리 가져오기 및 DB 저장
            insert_query = f"""
                INSERT INTO {table_name} (planet_code, reg_date, distance)
                VALUES (%s, %s, %s)
            """
            for day_data in horizons_data:
                delta = float(day_data["delta"])
                date = datetime.strptime(day_data["time"], "%Y-%b-%d %H:%M")

                # 가장 짧은 거리 찾기
                if delta < min_distance:
                    min_distance = delta
                    closest_date = date

                cursor.execute(insert_query, (planet_code, date, delta))
            conn.commit()

    except Exception as e:
        return {"error": f"DB 작업 중 에러 발생: {e}"}
    finally:
        if cursor is not None:
            cursor.close()

    if closest_date is None:
        return {"error": "Failed to find opposition event."}

    # closest_date를 datetime 객체로 변환하여 strftime 사용 가능하게 변경
    closest_date_str = closest_date.strftime("%Y-%m-%d")

    # 가시성 정보 데이터 정리
    visibility_data = {
        "best_time": visibility_info[0].get("best_time", "N/A"),
        "visible": visibility_info[0].get("visible", False),
        "right_ascension": visibility_info[0].get("right_ascension", "N/A"),
        "declination": visibility_info[0].get("declination", "N/A"),
        "visibility_judgment": visibility_info[0].get("visibility_judgment", "N/A")
    }

    return {
        "planet": planet_name,
        "closest_date": closest_date_str,
        "distance_to_earth": f"{min_distance:.2f} AU",
        "visibility": visibility_data,
        "timeZoneId": timezone_id,
        "offset_sec": offset_sec
    }


__all__ = ['predict_opposition_events_with_visibility']
