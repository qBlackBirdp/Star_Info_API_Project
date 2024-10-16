# services/planet_event_storage_service.py

import logging
from datetime import datetime, timedelta
from app.services.horizons_service import get_planet_position_from_horizons
from config_loader import load_db_config
import mysql.connector
import calendar

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

DB_CONFIG = load_db_config()


def store_planet_event(planet_name, event_date, distance):
    logging.info("===================store_planet_event 작동=======================")
    logging.info(f"행성 이름: {planet_name}, 날짜: {event_date}, 거리: {distance}")
    conn = None
    cursor = None
    try:
        logging.info("DB 연결 시도 중...")
        conn = mysql.connector.connect(**DB_CONFIG)
        logging.info("DB 연결 성공")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO planet_opposition_events (planet_name, date, distance)
            VALUES (%s, %s, %s)
        ''', (planet_name, event_date.strftime('%Y-%m-%d'), distance))
        conn.commit()
        logging.info("데이터 저장 성공")
    except mysql.connector.Error as err:
        logging.error(f"DB 에러 발생: {err}")
    except Exception as e:
        logging.error(f"기타 예외 발생: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        logging.info("===================정보 저장 로직 끝=======================")


def fetch_stored_event(planet_name, target_date):
    logging.info("===================fetch_stored_event 작동=======================")
    logging.info(f"행성 이름: {planet_name}, 검색 날짜: {target_date}")
    conn = None
    cursor = None
    row = None
    try:
        logging.info("DB 연결 시도 중...")
        conn = mysql.connector.connect(**DB_CONFIG)
        logging.info("DB 연결 성공")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date, distance FROM planet_opposition_events
            WHERE planet_name = %s AND date = %s
        ''', (planet_name, target_date.strftime('%Y-%m-%d')))
        row = cursor.fetchone()
        if row:
            logging.info(f"검색된 데이터: {row}")
        else:
            logging.info("해당 날짜에 대한 데이터 없음")
    except mysql.connector.Error as err:
        logging.error(f"DB 에러 발생: {err}")
    except Exception as e:
        logging.error(f"기타 예외 발생: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        logging.info("===================정보 불러오기 로직 끝=======================")

    if row:
        return {
            'planet_name': planet_name,
            'date': row[0],
            'distance': row[1]
        }
    return None


def calculate_and_store_opposition_event(planet_name, start_date, end_date):
    logging.info("===================calculate_and_store_opposition_event 작동=======================")
    logging.info(f"행성 이름: {planet_name}, 시작 날짜: {start_date}, 종료 날짜: {end_date}")
    current_date = start_date

    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        last_day_of_month = calendar.monthrange(year, month)[1]
        month_end_date = current_date.replace(day=last_day_of_month)

        if month_end_date > end_date:
            month_end_date = end_date

        logging.info(f"현재 날짜: {current_date}, 월 말 날짜: {month_end_date}")
        planet_data = get_planet_position_from_horizons(planet_name, current_date, (month_end_date - current_date).days)
        logging.info(f"Horizons API 응답 데이터: {planet_data}")

        if 'error' in planet_data:
            logging.error("Horizons API 데이터 가져오기 실패")
            raise ValueError("Failed to retrieve planet data from Horizons API.")

        horizons_data = planet_data.get('data')
        if not horizons_data:
            logging.error("Horizons API로부터 유효한 데이터 없음")
            raise ValueError("No valid data from Horizons API.")

        for day_data in horizons_data:
            delta = float(day_data['delta'])
            date = datetime.strptime(day_data['time'], '%Y-%b-%d %H:%M')
            logging.info(f"저장할 데이터 - 날짜: {date}, 거리: {delta}")
            store_planet_event(planet_name, date, delta)

        current_date = month_end_date + timedelta(days=1)

    logging.info("===================calculate_and_store_opposition_event 로직 끝=======================")


__all__ = ['store_planet_event', 'fetch_stored_event',
           'calculate_and_store_opposition_event']
