# services/planet_event_storage_service.py

import logging
from datetime import datetime, timedelta
from app.services.horizons_service import get_planet_position_from_horizons
import calendar
from global_db_connection import get_db_connection

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def store_planet_event(planet_name, event_date, distance):
    logging.info("===================store_planet_event 시작=======================")
    # 날짜 데이터 포맷팅
    db_date = str(event_date.strftime('%Y-%m-%d'))

    # 테이블 이름 동적 생성
    year = event_date.year
    table_name = f"{planet_name.lower()}_{year}_opposition_events"

    # 전역 DB 연결 가져오기
    conn = get_db_connection()
    if conn is None:
        logging.error("DB 연결을 사용할 수 없습니다.")
        return

    cursor = None
    try:
        cursor = conn.cursor()
        insert_query = f'''
            INSERT INTO {table_name} (planet_code, reg_date, distance)
            VALUES (%s, %s, %s)
        '''
        planet_code = get_planet_code(planet_name)  # 행성 코드 가져오기
        cursor.execute(insert_query, (planet_code, db_date, distance))
        conn.commit()
        logging.info("데이터 저장 성공")
    except Exception as e:
        logging.error(f"==DB 작업 중 에러 발생==: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        logging.info("===================store_planet_event 끝=======================")


def fetch_stored_event(planet_name, target_date):
    logging.info("===================fetch_stored_event 시작======================")
    # 날짜 데이터 포맷팅
    db_date = target_date.strftime('%Y-%m-%d')

    # 테이블 이름 동적 생성
    year = target_date.year
    table_name = f"{planet_name.lower()}_{year}_opposition_events"

    # 전역 DB 연결 가져오기
    conn = get_db_connection()
    if conn is None:
        logging.error("DB 연결을 사용할 수 없습니다.")
        return

    cursor = None
    row = None
    try:
        select_query = f'''
            SELECT reg_date, distance FROM {table_name}
            WHERE planet_code = %s AND reg_date = %s
        '''
        planet_code = get_planet_code(planet_name)  # 행성 코드 가져오기
        cursor = conn.cursor()
        cursor.execute(select_query, (planet_code, db_date))
        row = cursor.fetchone()
        if row:
            logging.info(f"검색된 데이터: {row}")
        else:
            logging.info("해당 날짜에 대한 데이터 없음")
    except Exception as e:
        logging.error(f"DB 작업 중 에러 발생: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        logging.info("===================fetch_stored_event 끝=======================")

    if row:
        return {
            'planet_name': planet_name,
            'reg_date': row[0],
            'distance': row[1]
        }
    return None


def get_planet_code(planet_name):
    planet_codes = {
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
    return planet_codes.get(planet_name)


def calculate_and_store_opposition_event(planet_name, start_date, end_date):
    logging.info("===================calculate_and_store_opposition_event 시작======================")
    current_date = start_date

    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        last_day_of_month = calendar.monthrange(year, month)[1]
        month_end_date = current_date.replace(day=last_day_of_month)

        if month_end_date > end_date:
            month_end_date = end_date

        planet_data = get_planet_position_from_horizons(planet_name, current_date, (month_end_date - current_date).days)

        if 'error' in planet_data:
            logging.error("Horizons API 데이터 가져오기 실패")
            raise ValueError("Failed to retrieve planet data from Horizons API.")

        horizons_data = planet_data.get('data')
        if not horizons_data:
            logging.error("Horizons API로부터 유효한 데이터 없음")
            raise ValueError("No valid data from Horizons API.")

        for day_data in horizons_data:
            try:
                delta = float(day_data['delta'])
                reg_date = datetime.strptime(day_data['time'], '%Y-%b-%d %H:%M')
                store_planet_event(planet_name, reg_date, delta)
            except ValueError as e:
                logging.error(f"데이터 변환 오류: {e}, 원본 데이터: {day_data}")
                continue

        current_date = month_end_date + timedelta(days=1)

    logging.info("===================calculate_and_store_opposition_event 끝======================")
