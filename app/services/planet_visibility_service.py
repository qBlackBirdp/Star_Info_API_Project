# services/planet_visibility_service.py

from datetime import datetime, timedelta

from skyfield import almanac
from skyfield.api import Topos

from app.global_resources import ts, planets  # 전역 리소스 임포트
from app.services.sunrise_sunset_service import calculate_sunrise_sunset_for_range  # 일출 및 일몰 계산 함수 import
from app.services.timezone_conversion_service import convert_utc_to_local_time  # 시간 변환 함수 import
from global_db_connection import get_db_connection
from app.services.horizons_service import get_planet_position_from_horizons


# Skyfield에서 사용하는 행성 이름과 코드 간의 매핑
def get_skyfield_planet_code(planet_name):
    planet_name_map = {
        "Mercury": "Mercury",
        "Venus": "Venus",
        "Earth": "Earth",
        "Mars": "Mars barycenter",
        "Jupiter": "Jupiter barycenter",
        "Saturn": "Saturn barycenter",
        "Uranus": "Uranus barycenter",
        "Neptune": "Neptune barycenter",
        "Pluto": "Pluto barycenter"
    }
    return planet_name_map.get(planet_name)


# DB에 저장할 행성 코드와 이름 간의 매핑
def get_db_planet_code(planet_name):
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


def calculate_planet_info(planet_name, latitude, longitude, date, range_days=1, timezone_info=None):
    """
    주어진 위치와 날짜에 대한 특정 행성의 가시성 및 위치 정보를 반환하는 함수
    """
    # 위치 설정
    location = Topos(latitude, longitude)

    # 타임존 정보가 제공되지 않은 경우, sunrise_sunset_data_list에서 가져옴
    if not timezone_info:
        sunrise_sunset_data_list = calculate_sunrise_sunset_for_range(latitude, longitude, date,
                                                                      date + timedelta(days=range_days - 1))
        if not sunrise_sunset_data_list or "error" in sunrise_sunset_data_list[0]:
            return [{"error": "Failed to calculate sunrise or sunset."}]

        timezone_info = {
            'timeZoneId': sunrise_sunset_data_list[0].get('timeZoneId', 'Unknown'),
            'offset_sec': sunrise_sunset_data_list[0].get('offset', 0)
        }

    # 지정된 범위에 대한 일출 및 일몰 정보 가져오기
    end_date = date + timedelta(days=range_days - 1)
    sunrise_sunset_data_list = calculate_sunrise_sunset_for_range(latitude, longitude, date, end_date)

    if not sunrise_sunset_data_list or "error" in sunrise_sunset_data_list[0]:
        return [{"error": "Failed to calculate sunrise or sunset."}]

    # DB에 저장할 행성 코드로 변환
    planet_code = get_db_planet_code(planet_name)
    if not planet_code:
        return [{"error": f"Invalid planet name: {planet_name}"}]

    # Skyfield에서 사용할 행성 이름으로 변환
    skyfield_planet_code = get_skyfield_planet_code(planet_name)
    if not skyfield_planet_code:
        return [{"error": f"Invalid planet name for Skyfield: {planet_name}"}]

    # 천체력에서 행성 가져오기
    planet = planets[skyfield_planet_code]

    # DB 연결 가져오기
    conn = get_db_connection()
    if conn is None:
        return [{"error": "Failed to connect to the database."}]

    # DB 연결 가져오기 및 필요한 테이블 생성 코드 추가
    cursor = None
    try:
        cursor = conn.cursor()
        # 테이블 생성 확인 및 생성
        table_name = f"{planet_name.lower()}_{date.year}_opposition_events"
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                planet_code INT NOT NULL,
                reg_date DATE NOT NULL,
                distance DOUBLE NOT NULL,
                s_o_t DOUBLE NOT NULL,
                right_ascension VARCHAR(20),
                declination VARCHAR(20)
            )
        """
        cursor.execute(create_table_query)

        # 데이터 조회 쿼리 추가
        select_query = f"""
            SELECT reg_date, distance, s_o_t, right_ascension, declination FROM {table_name}
            WHERE planet_code = %s AND reg_date BETWEEN %s AND %s
        """
        cursor.execute(select_query, (planet_code, date, end_date))
        rows = cursor.fetchall()

        if not rows:
            # 해당 연도 데이터가 없는 경우 Horizons API 요청
            year_start_date = datetime(date.year, 1, 1)
            year_end_date = datetime(date.year, 12, 31)

            planet_data = get_planet_position_from_horizons(planet_name, year_start_date,
                                                            (year_end_date - year_start_date).days)
            if 'error' in planet_data:
                return [{"error": f"Failed to retrieve planet data from Horizons API for {planet_name}"}]

            horizons_data = planet_data.get('data')
            if not horizons_data:
                return [{"error": "No valid data from Horizons API."}]

            # 가져온 데이터를 저장
            insert_query = f"""
                INSERT INTO {table_name} (planet_code, reg_date, distance, s_o_t, right_ascension, declination)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            for day_data in horizons_data:
                reg_date = datetime.strptime(day_data["time"], '%Y-%b-%d %H:%M')
                cursor.execute(insert_query, (
                    planet_code, reg_date, day_data.get('delta'), day_data.get('s-o-t'),
                    day_data.get('ra'), day_data.get('dec')
                ))

            conn.commit()

            # 저장 후 데이터 조회
            cursor.execute(select_query, (planet_code, date, end_date))
            rows = cursor.fetchall()

        results = []

        for row, sunrise_sunset_data in zip(rows, sunrise_sunset_data_list):
            reg_date, delta, s_o_t, ra, dec = row

            t0 = ts.utc(reg_date.year, reg_date.month, reg_date.day, 0, 0, 0)
            t1 = ts.utc(reg_date.year, reg_date.month, reg_date.day, 23, 59, 59)
            times, is_visible = almanac.find_discrete(t0, t1, almanac.risings_and_settings(planets, planet, location))

            # 가시성 판단 추가 로직
            visible = False
            best_time = None
            for t, visible_event in zip(times, is_visible):
                if visible_event == 1:  # 행성이 떠오르는 시간
                    visible = True
                    best_time = convert_utc_to_local_time(t.utc_datetime(), timezone_info['offset_sec']).time()
                    break

            # 일출 및 일몰 시간과 비교하여 관측 가능 여부 결정
            sunrise_time = datetime.fromisoformat(sunrise_sunset_data['sunrise']).time()
            sunset_time = datetime.fromisoformat(sunrise_sunset_data['sunset']).time()
            if best_time and (best_time < sunrise_time or best_time > sunset_time):
                visibility_judgment = f"Difficult to observe without special equipment (Best time: {best_time})"
            else:
                visibility_judgment = "Good visibility"

            results.append({
                "date": reg_date.strftime("%Y-%m-%d"),
                "visible": visible,
                "best_time": best_time.strftime("%H:%M") if best_time else "N/A",
                "timeZoneId": timezone_info['timeZoneId'],
                "offset_sec": timezone_info['offset_sec'],
                "distance_to_earth": f"{delta:.4f} AU" if delta else "N/A",
                "sun_observer_target_angle": f"{s_o_t:.2f}°" if s_o_t else "N/A",
                "right_ascension": ra if ra else "N/A",
                "declination": dec if dec else "N/A",
                "visibility_judgment": visibility_judgment
            })

    except Exception as e:
        return [{"error": f"Database operation failed: {e}"}]
    finally:
        if cursor:
            cursor.close()

    return results

