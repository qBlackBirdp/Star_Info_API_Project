# services/planet_opposition_service.py

from datetime import datetime
from app.services.planet_visibility_service import get_db_planet_code
import logging
from app.data.data import get_opposition_au_threshold
from global_db_connection import get_db_connection

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def predict_opposition_events(planet_name, year, strict=False):
    events_list = []

    # 연도의 시작과 끝 날짜 설정 (화성과 금성의 경우 2년치 데이터를 조회)
    if planet_name in ["Mars", "Venus"]:
        year_start_date = datetime(year, 1, 1)
        year_end_date = datetime(year + 1, 12, 31)
    else:
        year_start_date = datetime(year, 1, 1)
        year_end_date = datetime(year, 12, 31)

    # DB에서 대접근 이벤트를 찾기 위해 데이터 조회
    conn = get_db_connection()
    if conn is None:
        return {"error": "Failed to connect to the database."}

    cursor = None
    try:
        cursor = conn.cursor()

        # 두 해에 걸친 데이터를 UNION으로 결합하기 위해 테이블 설정
        if planet_name in ["Mars", "Venus"]:
            table_name_1 = f"{planet_name.lower()}_{year}_raw_data"
            table_name_2 = f"{planet_name.lower()}_{year + 1}_raw_data"

            select_query = f"""
                SELECT reg_date, distance, s_o_t FROM (
                    SELECT * FROM {table_name_1}
                    UNION ALL
                    SELECT * FROM {table_name_2}
                ) AS combined_data
                WHERE planet_code = %s AND reg_date BETWEEN %s AND %s AND distance <= %s
                ORDER BY distance ASC
                LIMIT 5
            """
        else:
            table_name = f"{planet_name.lower()}_{year}_raw_data"
            select_query = f"""
                SELECT reg_date, distance, s_o_t FROM {table_name}
                WHERE planet_code = %s AND reg_date BETWEEN %s AND %s AND distance <= %s
                ORDER BY distance ASC
                LIMIT 5
            """

        planet_code = get_db_planet_code(planet_name)
        threshold_strict = get_opposition_au_threshold(planet_name, strict=True)
        cursor.execute(select_query,
                       (planet_code, year_start_date, year_end_date, get_opposition_au_threshold(planet_name, strict)))
        rows = cursor.fetchall()

        if not rows:
            return {"error": "No opposition events found for the requested year."}

        for closest_event in rows:
            reg_date, distance, s_o_t = closest_event
            event_type = "planet big approach" if distance <= threshold_strict else "planet approach"
            events_list.append({
                "planet": planet_name,
                "closest_date": reg_date.strftime("%Y-%m-%d"),
                "distance_to_earth": f"{distance:.4f} AU",
                "sun_observer_target_angle": f"{s_o_t:.2f}°",
                "event_type": event_type
            })

    except Exception as e:
        return {"error": f"Database operation failed: {e}"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return events_list if events_list else {"error": "No opposition events found for the requested year."}


__all__ = ['predict_opposition_events']
