# services/planet_event_storage_service.py

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from global_db_connection import get_db_connection
from app.services.planets.planet_visibility_service import get_db_planet_code
from app.services.horizons_service import get_planet_position_from_horizons

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def update_raw_data():
    """
    모든 행성에 대해 현재 연도와 다음 연도의 대접근 이벤트 데이터를 업데이트하는 함수
    """
    planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    current_year = datetime.now().year + 2

    # DB 연결 가져오기
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database.")
        return

    cursor = None
    try:
        cursor = conn.cursor()
        for planet in planets:
            try:
                # 모든 행성에 대해 현재 연도와 다음 연도의 대접근 이벤트를 업데이트
                years_to_update = [current_year, current_year + 1]

                for year in years_to_update:
                    logging.info(f"Updating raw data for {planet} for the year {year}")

                    # Horizons API를 사용해 해당 연도의 데이터 가져오기
                    year_start_date = datetime(year, 1, 1)
                    year_end_date = datetime(year, 12, 31)
                    planet_data = get_planet_position_from_horizons(planet, year_start_date, (year_end_date - year_start_date).days)

                    if 'error' in planet_data:
                        logging.error(f"Failed to retrieve planet data from Horizons API for {planet}: {planet_data['error']}")
                        continue

                    horizons_data = planet_data.get('data')
                    if not horizons_data:
                        logging.error(f"No valid data from Horizons API for {planet} in year {year}.")
                        continue

                    # 가져온 데이터를 저장
                    table_name = f"{planet.lower()}_{year}_raw_data"
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

                    insert_query = f"""
                        INSERT INTO {table_name} (planet_code, reg_date, distance, s_o_t)
                        VALUES (%s, %s, %s, %s)
                    """
                    for day_data in horizons_data:
                        reg_date = datetime.strptime(day_data["time"], '%Y-%b-%d %H:%M')
                        cursor.execute(insert_query, (
                            get_db_planet_code(planet),
                            reg_date,
                            float(day_data.get('delta')),
                            float(day_data.get('s-o-t'))
                        ))

                    conn.commit()

            except Exception as e:
                logging.error(f"Failed to update raw data for {planet}: {e}")

    except Exception as e:
        logging.error(f"Database operation failed: {e}")
    finally:
        if cursor:
            cursor.close()
        conn.close()


# 스케줄링 설정
scheduler = BackgroundScheduler()
scheduler.add_job(update_raw_data, 'cron', month='1', day='1', hour='0', minute='0')
scheduler.start()
