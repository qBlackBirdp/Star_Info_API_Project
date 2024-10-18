# services/planet_visibility_service.py

from datetime import datetime, timedelta
from skyfield.api import Topos
from skyfield import almanac
from app.global_resources import ts, planets  # 전역 리소스 임포트
from app.services.timezone_conversion_service import convert_utc_to_local_time  # 시간 변환 함수 import
from app.services.sunrise_sunset_service import calculate_sunrise_sunset_for_range  # 일출 및 일몰 계산 함수 import
from app.services.horizons_service import get_planet_position_from_horizons  # NASA JPL Horizons API 데이터 호출 함수 import
from global_db_connection import get_db_connection


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


def calculate_planet_info(planet_name, latitude, longitude, date, range_days=1):
    """
    주어진 위치와 날짜에 대한 특정 행성의 가시성 및 위치 정보를 반환하는 함수

    Args:
        planet_name (str): 행성 이름 (예: "Mars")
        latitude (float): 위도
        longitude (float): 경도
        date (datetime): 가시성을 계산할 날짜
        range_days (int): 날짜 범위 (기본값: 1일)

    Returns:
        list: 행성의 가시성, 위치 정보 및 기타 세부사항을 포함한 딕셔너리 리스트
    """
    # 위치 설정
    location = Topos(latitude, longitude)



    # 지정된 범위에 대한 일출 및 일몰 정보 가져오기
    end_date = date + timedelta(days=range_days - 1)
    sunrise_sunset_data_list = calculate_sunrise_sunset_for_range(latitude, longitude, date, end_date)

    if not sunrise_sunset_data_list or "error" in sunrise_sunset_data_list[0]:
        return [{"error": "Failed to calculate sunrise or sunset."}]

    # 타임존 ID 정보 가져오기
    timezone_id = sunrise_sunset_data_list[0].get('timeZoneId', 'Unknown')

    # DB에 저장할 행성 코드로 변환
    planet_code = get_db_planet_code(planet_name)
    if not planet_code:
        return [{"error": f"Invalid planet name: {planet_name}"}]

    # Skyfield에서 사용할 행성 이름으로 변환
    skyfield_planet_code = get_skyfield_planet_code(planet_name)
    if not skyfield_planet_code:
        return [{"error": f"Invalid planet name for Skyfield: {planet_name}"}]

    # DB 연결 가져오기
    conn = get_db_connection()
    if conn is None:
        return [{"error": "DB 연결을 사용할 수 없습니다."}]

    cursor = None
    try:
        cursor = conn.cursor()
        table_name = f"{planet_name.lower()}_{date.year}_opposition_events"

        # 테이블이 존재하는지 확인하고, 없다면 생성
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                planet_code INT NOT NULL,
                reg_date DATE NOT NULL,
                distance DOUBLE NOT NULL,
                s_o_t DOUBLE NOT NULL
            )
        """
        cursor.execute(create_table_query)

        # 데이터 조회
        select_query = f"""
            SELECT reg_date, distance, s_o_t FROM {table_name}
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

            if "error" in planet_data:
                return [{"error": "Failed to retrieve planet data from Horizons API."}]

            horizons_data = planet_data.get("data")
            if not horizons_data:
                return [{"error": "No valid data from Horizons API."}]

            # 각 날짜의 거리 가져오기 및 DB 저장
            insert_query = f"""
                INSERT INTO {table_name} (planet_code, reg_date, distance, s_o_t)
                VALUES (%s, %s, %s, %s)
            """
            for day_data in horizons_data:
                delta = float(day_data["delta"])
                s_o_t = float(day_data["s-o-t"])
                reg_date = datetime.strptime(day_data["time"], "%Y-%b-%d %H:%M")

                # 로그 추가: 삽입 데이터 확인
                # print(f"Inserting data - planet_code: {planet_code}, reg_date: {reg_date}, distance: {delta}, s_o_t: {s_o_t}")

                try:
                    cursor.execute(insert_query, (planet_code, reg_date, delta, s_o_t))
                except Exception as e:
                    print(f"Insert Error: {e}")

            conn.commit()
            print("Data committed successfully")

            # 새로 저장된 데이터를 조회
            cursor.execute(select_query, (planet_code, date, end_date))
            rows = cursor.fetchall()

        results = []

        for row, sunrise_sunset_data in zip(rows, sunrise_sunset_data_list):
            reg_date, delta, s_o_t = row
            current_date = reg_date

            # 타임존 오프셋 및 일출, 일몰 시간 가져오기
            offset_sec = sunrise_sunset_data.get("offset")
            if offset_sec is None:
                results.append({"error": "Failed to retrieve timezone offset."})
                continue

            sunrise_time = datetime.fromisoformat(sunrise_sunset_data["sunrise"]).time()
            if sunrise_time is None:
                results.append({"error": "Failed to retrieve sunrise_time."})
                continue

            sunset_time = datetime.fromisoformat(sunrise_sunset_data["sunset"]).time()

            # 천체력에서 행성 가져오기
            planet = planets[skyfield_planet_code]

            # 관측 시간 설정
            t0 = ts.utc(current_date.year, current_date.month, current_date.day - 1, 0, 0, 0)
            t1 = ts.utc(current_date.year, current_date.month, current_date.day + 1, 0, 0, 0)
            times, is_visible = almanac.find_discrete(t0, t1, almanac.risings_and_settings(planets, planet, location))

            # 가시성 판단 추가 로직
            visibility_judgment = "Unknown"
            if delta < 1.5 and s_o_t > 30:
                visibility_judgment = "Good visibility"
            elif 1.5 <= delta < 2.5 and s_o_t > 20:
                visibility_judgment = "Moderate visibility"
            else:
                visibility_judgment = "Poor visibility"

            # 가장 좋은 관측 시간과 가시성 여부 설정
            visible = False
            best_time = None
            for t, visible_event in zip(times, is_visible):
                if visible_event == 1:  # 행성이 떠오르는 시간
                    visible = True
                    best_time = convert_utc_to_local_time(t.utc_datetime(), offset_sec).time()

                    # 낮 시간대인지 여부 판별
                    if sunrise_time <= best_time <= sunset_time:
                        visible = False
                        best_time = f"낮 시간대 (특수 장비 없이 관측 힘듦, 시간: {best_time.strftime('%H:%M')})"
                    break

            if best_time is None:
                best_time = "N/A"

            # 결과 추가
            results.append({
                "planet": planet_name,
                "date": current_date.strftime("%Y-%m-%d"),
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "visible": visible,
                "best_time": best_time if isinstance(best_time, str) else best_time.strftime("%H:%M"),
                "right_ascension": f"N/A",  # 현재는 Horizons 데이터 없이 DB 기반으로만 사용하기 때문에 적경 값을 알 수 없음
                "declination": f"N/A",  # 적위 값도 Horizons 데이터 없이 알 수 없음
                "distance_to_earth": f"{delta:.4f} AU",  # 지구와의 거리 추가
                "sun_observer_target_angle": f"{s_o_t:.2f}°",  # 태양-관측자-행성 각도 추가
                "visibility_judgment": visibility_judgment,  # 가시성 판단 추가
                "timeZoneId": timezone_id  # 타임존 ID 추가
            })

    except Exception as e:
        return [{"error": f"DB 작업 중 에러 발생: {e}"}]
    finally:
        if cursor is not None:
            cursor.close()

    return results
